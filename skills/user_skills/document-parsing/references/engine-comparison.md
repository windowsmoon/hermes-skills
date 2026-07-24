# MinerU vs PaddleOCR — Comparison Notes

Extracted from conversation with user who needs PPT/scan-PDF → Markdown → Obsidian pipeline.

## Quick Decision

| Your need | Pick |
|-----------|------|
| PDF + images → Markdown | MinerU ✅ |
| PPT/DOCX/XLSX → Markdown | MinerU ✅ (PaddleOCR: ❌ no native PPT/DOCX/XLSX) |
| Highest OCR accuracy on Chinese text | PaddleOCR (dedicated OCR engine) |
| Fastest first-time setup | MinerU (simpler deps) |
| CPU-only machine | Either works (MinerU: `-b pipeline`, PaddleOCR: native) |

## MinerU (opendatalab/MinerU)

- **Repo**: github.com/opendatalab/MinerU — 74.9k ⭐
- **CLI**: `mineru -p <input> -o <output>`
- **Inputs**: PDF, PNG, JPG, PPTX, DOCX, XLSX
- **Outputs**: Markdown (default) or JSON (`--json`)
- **Backends**: Auto (GPU if available), `pipeline` (CPU fallback)
- **Models**: ~2GB, auto-download from HuggingFace or ModelScope
- **Install**: `pip install "mineru[all]"`
- **License**: MIT (core) + commercial options for enterprise
- **CPU mode**: `mineru -p input.pdf -o out/ -b pipeline`

## PaddleOCR (PaddlePaddle/PaddleOCR)

- **Repo**: github.com/PaddlePaddle/PaddleOCR — 85.7k ⭐
- **CLI**: `paddleocr --image_dir=<dir> --type=structure`
- **Inputs**: PDF, images only (no PPT/DOCX/XLSX)
- **Outputs**: Markdown, JSON, DOCX
- **Backends**: CPU/GPU/XPU/NPU
- **Models**: ~500MB+ (PP-OCR series) or ~2GB (PaddleOCR-VL)
- **Install**: `pip install paddleocr`
- **License**: Apache 2.0
- **Key strength**: SOTA Chinese OCR with 109 language support, fine-grained coordinate output

## Test Methodology

When deciding which engine to try first on a user's document:

1. Check file extension
2. If .pptx / .docx / .xlsx → MinerU is the only option
3. If scanned PDF → try MinerU first (simpler), fall back to PaddleOCR if quality is poor
4. If digital PDF → MinerU handles text extraction natively
5. If image-heavy + high OCR accuracy critical → PaddleOCR

## First-Run Gotchas

- MinerU downloads ~2GB on first `mineru` invocation. Set a 900s timeout.
- PaddleOCR downloads models on first `paddleocr` call. Similar ~5-15min first run.
- For users behind Great Firewall: set `MINERU_MODEL_SOURCE=modelscope` or use `paddleocr` with `--use_gpu False`.
