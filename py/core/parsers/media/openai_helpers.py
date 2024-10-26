import logging
import requests
import json

logger = logging.getLogger()


# Define a function to log usage in a special format
def log_usage(api_type: str, token_usage: int, success: bool):
    log_message = f"USAGE_LOG | type={api_type} | tokens={token_usage} | success={success}"
    logger.info(log_message)


def process_frame_with_openai(
    data: bytes,
    api_key: str,
    model: str = "gpt-4o",
    max_tokens: int = 2048,
    api_base: str = "https://api.openai.com/v1/chat/completions",
) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "First, provide a title for the image, then explain everything that you see. Be very thorough in your analysis as a user will need to understand the image without seeing it. If it is possible to transcribe the image to text directly, then do so. The more detail you provide, the better the user will understand the image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{data}"},  # type: ignore
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(api_base, headers=headers, json=payload)
        response_json = response.json()

        if "choices" not in response_json or not response_json["choices"]:
            raise ValueError("Unexpected API response structure.")

        content = response_json["choices"][0]["message"]["content"]

        # Assuming token usage is available in the response, otherwise set it to 0
        token_usage = response_json.get("usage", {}).get("total_tokens", 0)

        # Log usage for successful requests
        log_usage(
            api_type="image_processing", token_usage=token_usage, success=True
        )

        # print("OpenAI process_frame_with_openai response: ", response_json)
        return content

    except (requests.RequestException, KeyError, ValueError) as e:
        # Log the failure and token usage as 0
        log_usage(api_type="image_processing", token_usage=0, success=False)
        logger.error(f"Failed to process frame with OpenAI: {str(e)}")
        return "Error processing image."


def process_audio_with_openai(
    audio_file,
    api_key: str,
    audio_api_base: str = "https://api.openai.com/v1/audio/transcriptions",
) -> str:
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": "whisper-1"}
    files = {"file": (audio_file.name, audio_file, "audio/wav")}

    try:
        transcription_response = requests.request(
            "POST", audio_api_base, headers=headers, data=payload, files=files
        )
        transcription = transcription_response.json()

        if "text" not in transcription:
            raise ValueError("Unexpected API response structure.")

        # Log successful transcription (assuming token usage or some similar metric is available)
        log_usage(api_type="audio_processing", token_usage=0, success=True)

        # print("OpenAI process_audio_with_openai response: ", transcription)
        return transcription["text"]

    except (requests.RequestException, KeyError, ValueError) as e:
        # Log the failure and token usage as 0
        log_usage(api_type="audio_processing", token_usage=0, success=False)
        logger.error(f"Failed to process audio with OpenAI: {str(e)}")
        return "Error processing audio."
