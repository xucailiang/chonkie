"""Neural Chunking for Chonkie API."""

import os
from typing import Dict, List, Optional, Union, cast

import requests

from chonkie.types import Chunk

from .base import CloudChunker


class NeuralChunker(CloudChunker):
    """Neural Chunking for Chonkie API."""

    BASE_URL = "https://api.chonkie.ai"
    VERSION = "v1"
    DEFAULT_MODEL = "mirth/chonky_modernbert_large_1"

    SUPPORTED_MODELS = [
        "mirth/chonky_distilbert_base_uncased_1",
        "mirth/chonky_modernbert_base_1",
        "mirth/chonky_modernbert_large_1",
    ]

    SUPPORTED_MODEL_STRIDES = {
        "mirth/chonky_distilbert_base_uncased_1": 256,
        "mirth/chonky_modernbert_base_1": 512,
        "mirth/chonky_modernbert_large_1": 512,
    }

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        min_characters_per_chunk: int = 10,
        stride: Optional[int] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the NeuralChunker."""
        self.api_key = api_key or os.getenv("CHONKIE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Please set the CHONKIE_API_KEY environment variable "
                + "or pass an API key to the NeuralChunker constructor."
            )

        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Model {model} is not supported. Please choose from one of the following: {self.SUPPORTED_MODELS}"
            )
        if min_characters_per_chunk < 1:
            raise ValueError("Minimum characters per chunk must be greater than 0.")

        self.model = model
        self.min_characters_per_chunk = min_characters_per_chunk
        self.stride = stride

        # Check if the Chonkie API is reachable
        try:
            response = requests.get(f"{self.BASE_URL}/")
            if response.status_code != 200:
                raise ValueError(
                    "Oh no! You caught Chonkie at a bad time. It seems to be down right now. Please try again in a short while."
                    + "If the issue persists, please contact support at support@chonkie.ai."
                )
        except Exception as error:
            raise ValueError(
                "Oh no! You caught Chonkie at a bad time. It seems to be down right now. Please try again in a short while."
                + "If the issue persists, please contact support at support@chonkie.ai."
            ) from error

    def chunk(self, text: Union[str, List[str]]) -> Union[List[Chunk], List[List[Chunk]]]:
        """Chunk the text into a list of chunks."""
        # Create the payload
        payload = {
            "text": text,
            "model": self.model,
            "min_characters_per_chunk": self.min_characters_per_chunk,
            "stride": self.stride,
        }
        
        # Send the request to the Chonkie API
        try:
            response = requests.post(
                f"{self.BASE_URL}/{self.VERSION}/chunk/neural",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            if isinstance(text, list):
                batch_result: List[List[Dict]] = cast(List[List[Dict]], response.json())
                batch_chunks: List[List[Chunk]] = []
                for chunk_list in batch_result:
                    curr_chunks = []
                    for chunk in chunk_list:
                        curr_chunks.append(Chunk.from_dict(chunk))
                    batch_chunks.append(curr_chunks)
                return batch_chunks
            else:
                single_result: List[Dict] = cast(List[Dict], response.json())
                single_chunks: List[Chunk] = [Chunk.from_dict(chunk) for chunk in single_result]
                return single_chunks
        except Exception as error:
            raise ValueError(
                "Oh no! The Chonkie API returned an invalid response. Please ensure your input is correct and try again. "
                + "If the problem continues, contact support at support@chonkie.ai."
            ) from error

    def __call__(self, text: Union[str, List[str]]) -> Union[List[Chunk], List[List[Chunk]]]:
        """Call the NeuralChunker."""
        return self.chunk(text)
