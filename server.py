"""Local-only model service. Model downloads are a separate explicit command."""
import base64
import io
import os
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
models = {}
lock = Lock()
IDS = {'clip': 'openai/clip-vit-base-patch32', 'sam': 'Zigeng/SlimSAM-uniform-50'}


def load_model(kind):
    import torch
    from transformers import CLIPModel, CLIPProcessor, SamModel, SamProcessor
    if kind not in models:
        model_class, processor_class = (CLIPModel, CLIPProcessor) if kind == 'clip' else (SamModel, SamProcessor)
        device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
        location = str(ROOT / 'models' / kind)
        if not Path(location).is_dir():
            raise ValueError('模型未安装，请先运行 python download_models.py')
        model = model_class.from_pretrained(location, local_files_only=True).to(device).eval()
        processor = processor_class.from_pretrained(location, local_files_only=True)
        models[kind] = (model, processor, device)
    return models[kind]


def image_from_payload(data):
    raw = data.get('image', '')
    if not isinstance(raw, str) or not raw.startswith('data:image/jpeg;base64,'):
        raise ValueError('需要 JPEG 视频帧')
    image = Image.open(io.BytesIO(base64.b64decode(raw.split(',', 1)[1], validate=True)))
    if image.width * image.height > 4_000_000:
        raise ValueError('视频帧过大')
    return image.convert('RGB')


@app.before_request
def local_requests_only():
    if request.host not in ('127.0.0.1:8765', 'localhost:8765'):
        return jsonify(error='Invalid host'), 403
    origin = request.headers.get('Origin')
    if origin and origin not in ('http://127.0.0.1:8765', 'http://localhost:8765'):
        return jsonify(error='请从本地服务页面访问'), 403


@app.get('/')
def index():
    return send_from_directory(ROOT, 'index.html')


@app.get('/api/status')
def status():
    return jsonify(models={k: (ROOT / 'models' / k / 'config.json').exists() for k in IDS})


@app.post('/api/classify')
def classify():
    import torch
    data = request.get_json()
    labels = data.get('labels')
    if not isinstance(labels, list) or not 2 <= len(labels) <= 30 or any(not isinstance(x, str) or not x.strip() or len(x) > 200 for x in labels):
        raise ValueError('需要 2–30 个英文候选描述，每项不超过 200 字符')
    image = image_from_payload(data)
    with lock:
        model, processor, device = load_model('clip')
        inputs = processor(text=labels, images=image, return_tensors='pt', padding=True).to(device)
        with torch.inference_mode():
            scores = model(**inputs).logits_per_image.softmax(dim=-1)[0].cpu().tolist()
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return jsonify(index=order[0], score=scores[order[0]], margin=scores[order[0]]-scores[order[1]], model=IDS['clip'])


@app.post('/api/segment')
def segment():
    import numpy as np
    import torch
    data = request.get_json()
    image = image_from_payload(data)
    point = data.get('point')
    if not isinstance(point, list) or len(point) != 2 or any(not isinstance(x, (int, float)) for x in point) or not (0 <= point[0] < image.width and 0 <= point[1] < image.height):
        raise ValueError('分割提示点超出画面')
    with lock:
        model, processor, device = load_model('sam')
        inputs = processor(image, input_points=[[point]], return_tensors='pt').to(device)
        with torch.inference_mode():
            outputs = model(**inputs)
        masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs['original_sizes'].cpu(), inputs['reshaped_input_sizes'].cpu())[0][0]
        best = int(outputs.iou_scores[0, 0].argmax())
        mask = masks[best].numpy().astype(bool)
    rgba = np.zeros((image.height, image.width, 4), dtype=np.uint8)
    rgba[mask] = [40, 220, 180, 130]
    out = io.BytesIO()
    Image.fromarray(rgba).save(out, format='PNG')
    return jsonify(mask='data:image/png;base64,' + base64.b64encode(out.getvalue()).decode(), model=IDS['sam'])


@app.errorhandler(Exception)
def error(exc):
    from werkzeug.exceptions import HTTPException
    code = exc.code if isinstance(exc, HTTPException) else (400 if isinstance(exc, ValueError) else 500)
    return jsonify(error=str(exc)), code


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765, debug=False, threaded=True)
