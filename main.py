import cv2
from modules.cake import Cake

def main():
        fakecake = Cake('index.txt')
        fakecake.render()
        cv2.imwrite('./cake.jpg',fakecake.cake)
if __name__ == '__main__':
    main()


