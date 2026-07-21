import os
import yaml
import random
import argparse

def set_seed(seed):
    random.seed(seed)
    # torch.manual_seed(seed)
    print(f"Seed set to {seed}")

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def train(config_path, resume_checkpoint=None):
    config = load_config(config_path)
    seed = config.get('seed', 42)
    set_seed(seed)
    
    epochs = config.get('epochs', 10)
    batch_size = config.get('batch_size', 32)
    
    print(f"Starting training for {epochs} epochs with batch size {batch_size}")
    
    start_epoch = 0
    if resume_checkpoint and os.path.exists(resume_checkpoint):
        print(f"Resuming from checkpoint {resume_checkpoint}")
        # dummy load logic
        start_epoch = 5
        
    for epoch in range(start_epoch, epochs):
        print(f"Epoch {epoch}/{epochs} ...")
        # save checkpoint
        ckpt_path = f"checkpoint_epoch_{epoch}.pt"
        # torch.save(model.state_dict(), ckpt_path)
        print(f"Saved checkpoint to {ckpt_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config YAML')
    parser.add_argument('--resume', type=str, default=None, help='Path to checkpoint to resume from')
    args = parser.parse_args()
    
    train(args.config, args.resume)
