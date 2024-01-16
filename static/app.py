import cv2
import torch
import os
from time import sleep

class TomatoDetector:
    def __init__(self, input_folder, output_folder, model_name):
        # Başlangıç değişkenleri tanımlanıyor: giriş ve çıkış klasör yolları ve model ismi
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.model = self.load_model(model_name)  # Model yükleniyor
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Cihaz tespiti (GPU veya CPU)
        print("Using Device: ", self.device)

    def load_model(self, model_name):
        # YOLOv5 modelini ultralytics'ten yükleniyor
       model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True).autoshape()
       return model

    def score_image(self, image_path):
        # Görüntüyü yükleyip, boyutunu değiştirme ve modele sokup tahmin alma
        image = cv2.imread(image_path)
        image = cv2.resize(image, (640, 640))

        self.model.to(self.device)  # Modeli doğru cihaza taşıma
        results = self.model([image])  # Görüntüyü modele verme
        print("Görüntü modele verildi")
        labels, cord, confidences = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1], results.xyxyn[0][:, -2]
        print(f"Etiketler: {labels}")
        print(f"Koordinatlar: {cord}")
        print(f"Doğruluk Oranları: {confidences}")

        # Konsola doğruluk oranlarını yazdır
        for label, confidence in zip(labels, confidences):
            if self.model.names[int(label)] == 'Tomato':
                print(f"{confidence:.0%} Tomato")
        return labels, cord, confidences

    def plot_boxes(self, results, image):
        # Görüntü üzerinde tahmin edilen nesneleri işaretleme
        labels, cord, confidences = results
        n = len(labels)
        x_shape, y_shape = image.shape[1], image.shape[0]
        for i in range(n):
            row = cord[i]
            if self.model.names[int(labels[i])] == 'Tomato':
                # Sadece 'tomato' etiketli nesneler için kutu çizme
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 0, 255)  # Kırmızı renk tanımı
                cv2.rectangle(image, (x1, y1), (x2, y2), bgr, 2)  # Kutuyu çizme
                label = f"{confidences[i]:.0%} Tomato"  # Doğruluk yüzdesi ile etiket oluşturma
                cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
        return image

    def process_new_images(self):
        # Giriş klasöründeki yeni görüntüleri sürekli olarak kontrol etme ve işleme
        processed_files = set()
        while True:
            for image_name in os.listdir(self.input_folder):
                
                if image_name not in processed_files:   
                    image_path = os.path.join(self.input_folder, image_name)
                    results = self.score_image(image_path)
                    processed_image = self.plot_boxes(results, cv2.imread(image_path))
                    output_path = os.path.join(self.output_folder, image_name)
                    cv2.imwrite(output_path, processed_image)  # İşlenmiş görüntüyü kaydetme
                    processed_files.add(image_name)  # İşlenen dosyalar listesine ekleme
            sleep(5)  # Her 5 saniyede bir yeni görüntüleri kontrol etme

# Kullanım örneği
detector = TomatoDetector(input_folder='nesne', output_folder='Tomato', model_name='best.pt')
detector.process_new_images()  # Sınıfı çağırarak süreci başlatma
