"""Train both MobileNetV2 and Decision Tree on identical fixed image splits."""
import argparse
from agroroute.deep_learning import train_and_evaluate

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',default='data/plant_leaves')
    parser.add_argument('--epochs',type=int,default=8)
    parser.add_argument('--batch-size',type=int,default=16)
    parser.add_argument('--limit',type=int,default=1000)
    parser.add_argument('--no-pretrained',action='store_true',help='Use random initialization (not recommended for small datasets)')
    args=parser.parse_args()
    result=train_and_evaluate(args.data,epochs=args.epochs,batch_size=args.batch_size,limit=args.limit,pretrained=not args.no_pretrained)
    print('Split:',result['split_counts'])
    print('MobileNetV2 test accuracy:',round(result['mobilenet']['accuracy']*100,2),'%')
    print('Decision Tree test accuracy:',round(result['decision_tree']['accuracy']*100,2),'%')
    print('Saved to models/mobile_net_v2/')
if __name__=='__main__': main()
