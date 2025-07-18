# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Orpheus-FastAPI Overview

This is a high-performance Text-to-Speech (TTS) server that provides an OpenAI-compatible API for speech synthesis using the Orpheus model. The system converts text to speech with support for 25 different voices across 8 languages and includes emotion tags for expressive audio generation.

## Development Commands

### Server Operations
```bash
# Start the FastAPI server
python app.py

# Start with specific host/port
uvicorn app:app --host 0.0.0.0 --port 5005 --reload

# Docker Compose setup (recommended)
cp .env.example .env  # Configure environment variables first
docker compose up --build
```

### Dependencies
```bash
# Install PyTorch with CUDA support (required first)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install other dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p outputs static
```

### Testing
```bash
# Run the test suite
python -m pytest tests/ -v

# Test specific components
python tests/test_speechpipe.py

# Stream test (manual verification)
python stream_test.py
```

## Architecture

### Core Components

**FastAPI Server (`app.py`)**
- Main HTTP server handling API requests
- OpenAI-compatible `/v1/audio/speech` endpoint
- Legacy `/speak` endpoint for compatibility
- Web UI interface at `/` and `/web/`
- Streaming audio endpoint `/v1/audio/speech/stream`
- Configuration management via `.env` files

**TTS Engine (`tts_engine/`)**
- `inference.py`: Token generation and API communication with external LLM servers
- `speechpipe.py`: Audio conversion pipeline using SNAC model to convert tokens to WAV audio

### External Dependencies

**LLM Inference Server (Required)**
The system requires a separate LLM inference server running the Orpheus model:
- **Docker Compose**: Automatically sets up llama.cpp server
- **Manual options**: LM Studio, llama.cpp server, GPUStack, or any OpenAI-compatible server
- **Model formats**: GGUF quantized models (Q2_K, Q4_K_M, Q8_0)

### Processing Flow

1. **Text Input** → Format prompt with voice prefix and special tokens
2. **Token Generation** → Send to external LLM inference server via streaming API
3. **Token Processing** → Convert LLM tokens to audio token IDs using custom mapping
4. **Audio Generation** → Use SNAC model to convert tokens to PCM audio data
5. **Output** → Return WAV audio file or streaming audio chunks

### Performance Optimizations

**Hardware Detection**
- Automatically detects GPU capabilities (VRAM, compute capability)
- High-end GPU mode: 16GB+ VRAM or compute capability 8.0+
- Adjusts parallel processing, batch sizes, and worker counts accordingly

**Audio Processing**
- Vectorized tensor operations with CUDA acceleration
- Memory-mapped file I/O for large audio stitching
- Crossfade audio segments for seamless playback
- Parallel batch processing for long texts

**Token Optimization**
- Context window: 49 tokens (7²) for mathematical alignment
- Processing batches: 7 tokens (Orpheus model standard)
- Repetition penalty fixed at 1.1 for optimal quality

## Configuration

### Environment Variables (.env file)
```bash
# Required
ORPHEUS_API_URL=http://localhost:5006/v1/completions  # LLM inference server URL

# Model Configuration - Option 1: Pre-converted GGUF
ORPHEUS_MODEL_NAME=Orpheus-3b-FT-Q8_0.gguf

# Model Configuration - Option 2: HuggingFace safetensors (new)
ORPHEUS_HF_REPO=dr-flex/orpheus-lena  # HF repo with safetensors
ORPHEUS_MODEL_TYPE=fp16                # fp16 or fp32

# Generation Parameters
ORPHEUS_MAX_TOKENS=8192
ORPHEUS_TEMPERATURE=0.6
ORPHEUS_TOP_P=0.9

# Server Settings
ORPHEUS_HOST=0.0.0.0
ORPHEUS_PORT=5005
ORPHEUS_API_TIMEOUT=120
ORPHEUS_SAMPLE_RATE=24000

# Performance Tuning (for 16-bit models)
LLAMA_THREADS=8
LLAMA_BATCH_SIZE=32768
LLAMA_CTX_SIZE=49152
```

### Multilingual Support
- **Default**: English model with 8 voices
- **Language-specific models**: Available for French, German, Korean, Hindi, Mandarin, Spanish, Italian
- **Configuration**: Change `ORPHEUS_MODEL_NAME` in `.env` to use language-specific models

## Voice System

### Available Voices by Language
- **English**: tara (default), leah, jess, leo, dan, mia, zac, zoe
- **French**: pierre, amelie, marie
- **German**: jana, thomas, max, lena
- **Korean**: 유나, 준서
- **Hindi**: ऋतिका
- **Mandarin**: 长乐, 白芷
- **Spanish**: javi, sergio, maria
- **Italian**: pietro, giulia, carlo

### Emotion Tags
Supported emotion expressions: `<laugh>`, `<sigh>`, `<chuckle>`, `<cough>`, `<sniffle>`, `<groan>`, `<yawn>`, `<gasp>`

## API Endpoints

### OpenAI-Compatible
- `POST /v1/audio/speech` - Generate speech (OpenAI compatible)
- `POST /v1/audio/speech/stream` - Streaming audio generation
- `GET /v1/audio/voices` - List available voices

### Legacy/Web
- `POST /speak` - Simple speech generation
- `GET /` - Web interface
- `POST /web/` - Web form submission

### Configuration
- `GET /get_config` - Current configuration
- `POST /save_config` - Update configuration
- `POST /restart_server` - Restart server with new config

## Development Guidelines

### Code Structure
- Follow existing patterns in `tts_engine/` for audio processing
- Use environment variables for configuration (loaded via `python-dotenv`)
- Implement proper error handling with descriptive messages
- Performance monitoring included via `PerformanceMonitor` class

### Adding New Voices
1. Update `AVAILABLE_VOICES` lists in `tts_engine/inference.py`
2. Add voice-to-language mappings in `VOICE_TO_LANGUAGE`
3. Update HTML template for voice selection UI

### Hardware Optimization
- GPU acceleration automatically detected and configured
- High-end GPU optimizations for RTX 4090 and similar
- CPU fallback mode with appropriate worker counts
- Memory management with caching for performance

## Deployment

### Docker (Recommended)
- Use provided `docker-compose.yml` for complete setup
- Includes both FastAPI server and llama.cpp inference server
- Automatic model download from Hugging Face

### Native Installation
- Requires Python 3.8-3.11 (3.12 not supported)
- CUDA-compatible GPU recommended
- External LLM inference server required