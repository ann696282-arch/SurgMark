"""Run once with internet access; no patient video is used."""
from pathlib import Path
from transformers import CLIPModel, CLIPProcessor, SamModel, SamProcessor

root = Path(__file__).resolve().parent / 'models'
for name, model_id, model_cls, processor_cls in [
    ('clip', 'openai/clip-vit-base-patch32', CLIPModel, CLIPProcessor),
    ('sam', 'Zigeng/SlimSAM-uniform-50', SamModel, SamProcessor),
]:
    print('Downloading', model_id, flush=True)
    model_cls.from_pretrained(model_id).save_pretrained(root / name, safe_serialization=True)
    processor_cls.from_pretrained(model_id).save_pretrained(root / name)
print('Models ready. Run python server.py')
