#!/bin/bash
set -e

# Check if using legacy GGUF model or new HF repo
if [ -n "${ORPHEUS_MODEL_NAME}" ] && [ -z "${ORPHEUS_HF_REPO}" ]; then
    # Legacy mode: Use pre-converted GGUF model
    GGUF_MODEL_PATH="/models/${ORPHEUS_MODEL_NAME}"
    echo "Using legacy GGUF model: ${GGUF_MODEL_PATH}"
else
    # New mode: Use converted model from HF repo
    HF_REPO_FILENAME="${ORPHEUS_HF_REPO//\//_}"
    MODEL_TYPE="${ORPHEUS_MODEL_TYPE:-fp16}"
    GGUF_MODEL_PATH="/models/gguf/${HF_REPO_FILENAME}_${MODEL_TYPE}.gguf"
    echo "Using converted model from HF repo: ${GGUF_MODEL_PATH}"
fi

# Wait for model to be available
echo "Waiting for GGUF model at: ${GGUF_MODEL_PATH}"
while [ ! -f "${GGUF_MODEL_PATH}" ]; do
    echo "Model not found yet, waiting..."
    sleep 5
done

echo "Model found! Starting llama.cpp server..."

# Execute llama.cpp server with the model
# Optimized for 16-bit models with higher memory requirements
exec llama-server \
    -m "${GGUF_MODEL_PATH}" \
    --host ${LLAMA_ARG_HOST:-0.0.0.0} \
    --port ${LLAMA_ARG_PORT:-5006} \
    --n-gpu-layers -1 \
    --threads ${LLAMA_THREADS:-8} \
    --batch-size ${LLAMA_BATCH_SIZE:-32768} \
    --ubatch-size ${LLAMA_UBATCH_SIZE:-16384} \
    --ctx-size ${LLAMA_CTX_SIZE:-49152} \
    --cont-batching \
    --timeout 100 \
    --mlock \
    --flash-attn \
    --parallel ${LLAMA_PARALLEL:-4} \
    --numa numactl \
    --threads-http ${LLAMA_THREADS_HTTP:-4} \
    --cache-type-k f16 \
    --cache-type-v f16