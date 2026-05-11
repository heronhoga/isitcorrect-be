from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

def transcribe(path: str):
    audio_array, sampling_rate = librosa.load(
        path,
        sr=16000
    )

    input_features = processor(
        audio_array,
        sampling_rate=sampling_rate,
        return_tensors="pt"
    ).input_features

    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(
        predicted_ids,
        skip_special_tokens=True
    )

    return transcription[0]