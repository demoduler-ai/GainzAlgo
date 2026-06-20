import pandas as pd

def get_kap_signals():

    print("FONKSİYON BAŞLADI")

    data = [
        {
            "Hisse": "THYAO",
            "Olay": "Yeni İş İlişkisi",
            "Etki": "Çok Pozitif",
            "Puan": 25
        },
        {
            "Hisse": "ASELS",
            "Olay": "Savunma Sözleşmesi",
            "Etki": "Çok Pozitif",
            "Puan": 30
        },
        {
            "Hisse": "AKBNK",
            "Olay": "Geri Alım Programı",
            "Etki": "Pozitif",
            "Puan": 15
        }
    ]

    df = pd.DataFrame(data)

    print(df)

    return df