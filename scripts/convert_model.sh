#!/bin/bash
set -e

# Environment variables
HF_REPO="${ORPHEUS_HF_REPO}"
MODEL_TYPE="${ORPHEUS_MODEL_TYPE:-fp16}"
HF_MODEL_DIR="/models/hf/${HF_REPO//\//_}"
GGUF_OUTPUT_DIR="/models/gguf"
GGUF_OUTPUT_FILE="${GGUF_OUTPUT_DIR}/${HF_REPO//\//_}_${MODEL_TYPE}.gguf"

echo "=== Orpheus Model Conversion Service ==="
echo "HuggingFace Repo: ${HF_REPO}"
echo "Model Type: ${MODEL_TYPE}"
echo "Output GGUF: ${GGUF_OUTPUT_FILE}"

# Check if GGUF already exists
if [ -f "${GGUF_OUTPUT_FILE}" ]; then
    echo "GGUF model already exists at ${GGUF_OUTPUT_FILE}, skipping conversion"
    exit 0
fi

# Check if HF model already downloaded
if [ ! -d "${HF_MODEL_DIR}" ]; then
    echo "Cloning model from HuggingFace..."
    git lfs install
    git clone "https://huggingface.co/${HF_REPO}" "${HF_MODEL_DIR}"
else
    echo "HuggingFace model already exists at ${HF_MODEL_DIR}"
fi

# Convert to GGUF
echo "Converting model to GGUF format..."
cd /app/llama.cpp

# Determine output type based on MODEL_TYPE
if [ "${MODEL_TYPE}" = "fp32" ]; then
    OUTTYPE="f32"
else
    OUTTYPE="f16"
fi

# Run conversion
python convert_hf_to_gguf.py \
    "${HF_MODEL_DIR}" \
    --outfile "${GGUF_OUTPUT_FILE}" \
    --outtype "${OUTTYPE}"

# Verify output
if [ -f "${GGUF_OUTPUT_FILE}" ]; then
    echo "✓ Conversion successful!"
    echo "GGUF model saved to: ${GGUF_OUTPUT_FILE}"
    ls -lh "${GGUF_OUTPUT_FILE}"
else
    echo "✗ Conversion failed!"
    exit 1
fi

echo "=== Conversion complete ==="