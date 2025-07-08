import torch
from diffusers import FluxPipeline

pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
pipe.to("mps")

prompt = "The full body of a lion. I want a good image that I can make a 3D model from."
image = pipe(
    prompt,
    guidance_scale=0.0,
    num_inference_steps=4,
    max_sequence_length=256,
    generator=torch.Generator("mps").manual_seed(0)
).images[0]
image.show()
image.save("lion.png")