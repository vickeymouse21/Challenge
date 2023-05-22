import re
import pandas as pd

# Membaca dataset kamus alay
kamus_alay = pd.read_csv("new_kamusalay.csv", encoding='latin1',header=None)
kamus_alay = kamus_alay.rename(columns={0:'Alay',1:'Baku'})

print(kamus_alay)

# Memetakan kata Alay menjadi key dan kata Baku menjadi value yang berkaitan satu sama lain
kamus_alay_map = dict(zip(kamus_alay['Alay'], kamus_alay['Baku']))

# Membaca dataset abusive words
kata_kasar = pd.read_csv("abusive.csv",encoding='latin1')

print(kata_kasar)

#Membuat kata-kata abusive menjadi "cencored" dengan membuat kolom baru
kata_kasar['Kata_Sensor'] = "cencored"

print(kata_kasar)

# Memetakan kata-kata ABUSIVE menjadi key dan kata "cencored" menjadi value yang berkaitan satu sama lain
kata_kasar_map = dict(zip(kata_kasar['ABUSIVE'], kata_kasar['Kata_Sensor']))

def normalize_alay(text):
    return ' '.join([kamus_alay_map[word]
    if
        word in kamus_alay_map 
    
    else
        word for word in text.split(' ')])

def normalize_abusive(text):
    return ' '.join([kata_kasar_map[word]
    if
        word in kata_kasar_map 
                
    else
        word for word in text.split(' ')])

def cleansing_kata(text):
    # Menghapus karakter non-alfanumerik
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Menghapus whitespace tambahan
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Mengubah semua huruf menjadi huruf kecil
    text = text.lower()

    # Menghilangkan URL
    text= re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)

    # Menghilangkan non alpha numeric
    text = re.sub('[^0-9a-zA-Z]+',' ',text)

    # Mengilangkan angka atau digit
    text = re.sub(r'\d+', ' ', text)

    # Menghilangkan enter
    text = re.sub('\n',' ',text)

    # Menghilangkan tab
    text = re.sub('\t',' ',text)

    # Menghilangkan kata RT
    text = re.sub('rt',' ',text)

    # Menghilangkan kata user
    text = re.sub('user',' ',text)

    # Menghilangkan whitespace
    text = text.strip()

    # Membuat map terhadap kata-kata "alay" dan mengubahnya menjadi kata baku
    text = normalize_alay(text)

    # Mengganti kata kasar dengan kata "cencored" yang telah didefinisikan sebelumnya
    text = normalize_abusive(text)
    
    return text

# Menjalankan function cleansing
def cleansing_data(text):
    text = cleansing_kata(text)
    text = normalize_alay(text)
    text = normalize_abusive(text)
    
    return text

df = pd.read_csv('data.csv', encoding='latin1')
df['Tweet'] = df['Tweet'].apply(cleansing_data)
df['Tweet']