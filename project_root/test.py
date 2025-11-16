
from huggingface_hub import snapshot_download
# change local_dir to the target folder inside your project
snapshot_download(repo_id="cropinailab/aksara_v1", local_dir="models/aksara_v1", repo_type="model")
print("Downloaded to models/aksara_v1")
PY
