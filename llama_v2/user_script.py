# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from pathlib import Path

import config
import torch
from argmax_sampling_model import ArgmaxSampling
from decoder_model import DecoderModel
from update_embeddings_model import UpdateEmbeddings


# Helper latency-only dataloader that creates random tensors with no label
class RandomDataLoader:
    def __init__(self, create_inputs_func, batch_size):
        self.create_input_func = create_inputs_func
        self.batch_size = batch_size

    def __getitem__(self, idx):
        label = None
        return self.create_input_func(self.batch_size), label


# -----------------------------------------------------------------------------
# ARGMAX SAMPLING
# -----------------------------------------------------------------------------


def load_argmax_sampling_model(model_path):
    model = ArgmaxSampling()
    model.eval()
    return model


def argmax_sampling_inputs(model):
    batch_size = 1
    vocab_size = 32000
    return torch.zeros((batch_size, vocab_size), dtype=torch.float16)


def argmax_sampling_data_loader(data_dir, batch_size, *args, **kwargs):
    return RandomDataLoader(argmax_sampling_inputs, batch_size)


# -----------------------------------------------------------------------------
# UPDATE EMBEDDINGS
# -----------------------------------------------------------------------------


def load_update_embeddings_model(model_path):
    vocab_size = 32000
    hidden_size = 4096
    model = UpdateEmbeddings(config.embeddings_file, vocab_size, hidden_size)
    model.eval()
    return model


def update_embeddings_inputs(model):
    seq_len = 10
    return torch.zeros((seq_len,), dtype=torch.int64)


def update_embeddings_data_loader(data_dir, batch_size, *args, **kwargs):
    return RandomDataLoader(update_embeddings_inputs, batch_size)


# -----------------------------------------------------------------------------
# DECODER
# -----------------------------------------------------------------------------


def get_or_create_decoder_model():
    num_layers = 32
    num_heads = 32
    vocab_size = 32000
    hidden_size = 4096
    scale_type = "SquareRootHeadDim"
    device = torch.device("cpu")

    # Lazily load the decoder model the first time it's requested. This is necessary because both the cache and
    # no_cache models need to share the same instance in order to export their common weights with the same names.
    # Not doing so would result identical weights having different names in both models, which makes merging them
    # very difficult.
    if config.decoder_model is None:
        config.decoder_model = DecoderModel(
            num_layers,
            vocab_size,
            hidden_size,
            num_heads,
            scale_type,
            device=device,
        )
        config.decoder_model.eval()

        script_dir = Path(__file__).resolve().parent
        weights_path = script_dir / "raw_model_data" / "7B-chat" / "llama-2-7b-chat.pth"

        # We don't use rope.freqs
        state_dict = torch.load(weights_path)
        del state_dict["rope.freqs"]
        config.decoder_model.load_state_dict(state_dict)

    return config.decoder_model


def load_decoder_model(model_path):
    model = get_or_create_decoder_model()
    model.set_use_cache(False)
    return model


def decoder_inputs(model):
    batch_size = 1
    seq_len = 10
    hidden_size = 4096
    max_seq_len = 2048
    num_layers = 32
    num_heads = 32
    head_size = hidden_size // num_heads

    return {
        "x": torch.rand((batch_size, seq_len, hidden_size), dtype=torch.float32),
        "attn_mask": torch.zeros((1, max_seq_len, max_seq_len), dtype=torch.int32),
        "cache": [
            {
                "key": torch.rand((batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32),
                "value": torch.rand((batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32),
            }
            for _ in range(num_layers)
        ],
    }


# -----------------------------------------------------------------------------
# DECODER WITH PAST
# -----------------------------------------------------------------------------


def load_decoder_with_past_model(model_path):
    model = get_or_create_decoder_model()
    model.set_use_cache(True)
    return model


def decoder_with_past_inputs(model):
    batch_size = 1
    hidden_size = 4096
    max_seq_len = 2048
    num_layers = 32
    num_heads = 32
    head_size = hidden_size // num_heads
    return {
        "x_increment": torch.rand((batch_size, 1, hidden_size), dtype=torch.float32),
        "attn_mask": torch.zeros((1, max_seq_len, max_seq_len), dtype=torch.int32),
        "cos": torch.rand((batch_size, max_seq_len, 1, 64), dtype=torch.float32),
        "sin": torch.rand((batch_size, max_seq_len, 1, 64), dtype=torch.float32),
        "cache": [
            {
                "key": torch.rand((batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32),
                "value": torch.rand((batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32),
            }
            for _ in range(num_layers)
        ],
    }


# -----------------------------------------------------------------------------
# MERGED DECODERS
# -----------------------------------------------------------------------------


def merged_decoders_inputs(model):
    batch_size = 1
    hidden_size = 4096
    max_seq_len = 2048
    num_layers = 32
    num_heads = 32
    head_size = hidden_size // num_heads
    seq_len = 10

    inputs = {
        "x": torch.rand((batch_size, seq_len, hidden_size), dtype=torch.float16),
        "attn_mask": torch.zeros((1, max_seq_len, max_seq_len), dtype=torch.int32),
    }

    for layer_idx in range(num_layers):
        inputs[f"cache.{layer_idx}.key"] = torch.rand(
            (batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32
        )
        inputs[f"cache.{layer_idx}.value"] = torch.rand(
            (batch_size, num_heads, max_seq_len, head_size), dtype=torch.float32
        )

    inputs["x_increment"] = torch.rand((batch_size, 1, hidden_size), dtype=torch.float16)
    inputs["cos"] = torch.rand((batch_size, max_seq_len, 1, 64), dtype=torch.float16)
    inputs["sin"] = torch.rand((batch_size, max_seq_len, 1, 64), dtype=torch.float16)
    inputs["use_cache_branch"] = torch.ones((1,), dtype=torch.bool)

    return inputs


def merged_decoders_data_loader(data_dir, batch_size, *args, **kwargs):
    return RandomDataLoader(merged_decoders_inputs, batch_size)
