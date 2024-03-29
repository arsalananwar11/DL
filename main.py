import argparse
import torchvision
from torchvision.transforms import ToTensor
from model import ResNet18
import torch.optim as optim
import torch
import torch.nn as nn


def get_args():
    parser = argparse.ArgumentParser(description="Training CIFAR10")
    parser.add_argument('--optimizer', dest="optimizer", default="SGD", type=str, help="optmizer type, defaults to SGD")
    parser.add_argument('--lr', dest="lr", default=0.03, type=float, help="learning rate")
    parser.add_argument('--momentum', dest="momentum", default=0.9, type=float, help="momentum (if applicable)")
    parser.add_argument('--weight-decay', dest="weight_decay", default=5e-4, type=float, help="weight decay (if applicable")
    parser.add_argument('--num-epochs', dest="num_epochs", default=10, type=int, help="number of epochs for test/train loops")
    return parser.parse_args()

def get_optimizer(model, optimizer, lr, momentum, weight_decay):
    if optimizer == "SGD":
        return optim.SGD(model.parameters(), lr=lr,
                      momentum=momentum, weight_decay=weight_decay)
    
    elif optimizer == "Adam":
        return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    
def train(model, iterator, optimizer, criterion, device):
    model.train()
    epoch_loss = 0
    correct = 0
    total = 0
    for batch_idx, (inputs, targets) in enumerate(iterator):
        print(f"Training Batch Index: {batch_idx}")
        optimizer.zero_grad()
        inputs = inputs.to(device)
        targets = targets.to(device)    

        outputs = model(inputs)
        
        
        loss = criterion(outputs, targets)
        
        epoch_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(targets).sum().item()
        total += targets.size(0)
        
        loss.backward()
        optimizer.step()
            
    return epoch_loss / len(iterator), correct / total

def test(model, iterator, criterion, device):
    
    # Q3c. Set up the evaluation function.
    epoch_loss = 0
    total = 0
    correct = 0
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(iterator):
            print(f"Evaluating Batch Index: {batch_idx}")
            inputs = inputs.to(device)
            targets = targets.to(device)    
            
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            epoch_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(targets).sum().item()
            total += targets.size(0)
            
        
    return epoch_loss / len(iterator), correct / total
        
    

def main():
    args = get_args()
    
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Using {device} device")
    
    # Load CIFAR10
    trainset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=ToTensor())
    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=128, shuffle=True)

    testset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=ToTensor())
    testloader = torch.utils.data.DataLoader(
        testset, batch_size=128, shuffle=False)
    
    model = ResNet18().to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = get_optimizer(model, args.optimizer, args.lr, args.momentum, args.weight_decay)
    
    train_output_file_name = f"train_run_optimizer={args.optimizer}_lr={args.lr}_momentum={args.momentum}_weightdecay={args.weight_decay}_numepochs={args.num_epochs}.csv"
    test_output_file_name = f"test_run_optimizer={args.optimizer}_lr={args.lr}_momentum={args.momentum}_weightdecay={args.weight_decay}_numepochs={args.num_epochs}.csv"

    
    with open(train_output_file_name, 'w') as outfile:
        fields = "epoch, train_loss, train_acc\n"
        outfile.write(fields)
    
        for epoch in range(1, args.num_epochs+1):
            print(f"Training loop for epoch: {epoch}")
            
            train_loss, train_acc = train(model, trainloader, optimizer, criterion, device)
            
            line = f"{epoch}, {train_loss}, {train_acc}\n"
            outfile.write(line)
            
            
    with open(test_output_file_name, 'w') as outfile:
        fields = "epoch, test_loss, test_acc\n"
        outfile.write(fields)
    
        for epoch in range(1, args.num_epochs+1):
            print(f"Testing loop for epoch: {epoch}")
            
            test_loss, test_acc = test(model, testloader, criterion, device)
            
            line = f"{epoch}, {test_loss}, {test_acc}\n"
            outfile.write(line)
        
        
    
    
    
if __name__ == "__main__":
    main()