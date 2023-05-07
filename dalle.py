import numpy as np
from tqdm import tqdm
from PIL import Image
import torch
from torch import autocast
from transformers import CLIPTextModel, CLIPTokenizer
from transformers import DPTForDepthEstimation, DPTFeatureExtractor
from diffusers import AutoencoderKL, UNet2DConditionModel
from diffusers.schedulers.scheduling_pndm import PNDMScheduler

class DiffusionPipeline:
    def __init__(self, 
                 vae, 
                 tokenizer, 
                 text_encoder, 
                 unet, 
                 scheduler):
        
        self.vae = vae
        self.tokenizer = tokenizer
        self.text_encoder = text_encoder
        self.unet = unet
        self.scheduler = scheduler
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def get_text_embeds(self, text):
        # tokenize the text
        text_input = self.tokenizer(text, 
                                    padding='max_length', 
                                    max_length=tokenizer.model_max_length, 
                                    truncation=True, 
                                    return_tensors='pt')
        # embed the text
        with torch.no_grad():
            text_embeds = self.text_encoder(text_input.input_ids.to(self.device))[0]
        return text_embeds

    def get_prompt_embeds(self, prompt):
        if isinstance(prompt, str):
            prompt = [prompt]
        # get conditional prompt embeddings
        cond_embeds = self.get_text_embeds(prompt)
        # get unconditional prompt embeddings
        uncond_embeds = self.get_text_embeds([''] * len(prompt))
        # concatenate the above 2 embeds
        prompt_embeds = torch.cat([uncond_embeds, cond_embeds])
        return prompt_embeds

    def decode_img_latents(self, img_latents):
        img_latents = 1 / self.vae.config.scaling_factor * img_latents
        with torch.no_grad():
            img = self.vae.decode(img_latents).sample
        
        img = (img / 2 + 0.5).clamp(0, 1)
        img = img.cpu().permute(0, 2, 3, 1).float().numpy()
        return img

    def transform_img(self, img):
        # scale images to the range [0, 255] and convert to int
        img = (img * 255).round().astype('uint8')
        # convert to PIL Image objects
        img = [Image.fromarray(i) for i in img]
        return img

    def encode_img_latents(self, img, latent_timestep):
        if not isinstance(img, list):
            img = [img]
        img = np.stack([np.array(i) for i in img], axis=0)
        # scale images to the range [-1, 1]
        img = 2 * ((img / 255.0) - 0.5)
        img = torch.from_numpy(img).float().permute(0, 3, 1, 2)
        img = img.to(self.device)
        # encode images
        img_latents_dist = self.vae.encode(img)
        img_latents = img_latents_dist.latent_dist.sample()
        # scale images
        img_latents = self.vae.config.scaling_factor * img_latents
        # add noise to the latents
        noise = torch.randn(img_latents.shape).to(self.device)
        img_latents = self.scheduler.add_noise(img_latents, noise, latent_timestep)
        return img_latents