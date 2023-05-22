import re # Memanggil regex
import sqlite3 # Memanggil package untuk database
import pandas as pd # Memanggil package untuk dataframe

from flask import Flask, jsonify, request # Memanggil flask
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from ##Memanggil Swagger

# KAMUS ALAY
# Membaca dataset kamus alay
kamus_alay = pd.read_csv("new_kamusalay.csv", encoding='latin1',header=None)
kamus_alay = kamus_alay.rename(columns={0:'Alay', 1:'Baku'})

# Memetakan kata Alay menjadi key dan kata Baku menjadi value yang berkaitan satu sama lain
kamus_alay_map = dict(zip(kamus_alay['Alay'], kamus_alay['Baku']))

# ABUSIVE WORDS
# Membaca dataset abusive words
kata_kasar = pd.read_csv("abusive.csv",encoding='latin1')

# Membuat kata-kata abusive menjadi "cencored" dengan membuat kolom baru
kata_kasar['Kata_Sensor'] = "cencored"

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

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder

# Merubah tulisan template halaman host 
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Cleasning Text Gold Challenge BINAR'),
        'version': LazyString(lambda: '1.0.0 // BETA'),
        'description': LazyString(lambda: 'API Documentation for Text Processing'),
    },
    host = LazyString(lambda: request.host)
)

# Konfigurasi alamat halaman akses, dll
swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'docs',
            'route': '/docs.json',
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route':'/'
}

# Menggabungkan template dan konfigurasi dalam satu variabel
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)


@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }

    response_data = jsonify(json_response)
    return response_data

    
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    #before
    text = request.form.get('text')

    #after
    text_clean = cleansing_data(text)

    #Input Database (db)
    with sqlite3.connect("Database_Challenge.db") as DB:
        DB.execute('CREATE TABLE if not exists cleansing (text_ori varchar(255), text_clean varchar(255))')
        query_txt = 'INSERT INTO cleansing (text_ori , text_clean) VALUES (?,?)'
        val = (text, text_clean)
        DB.execute(query_txt, val)
        DB.commit()


    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': text_clean,
    }

    response_data = jsonify(json_response)
    return response_data


@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file, encoding='latin-1')

    # Ambil teks yang akan diproses dalam format list

    # Sebelum Cleansing
    texts_kotor = df['Tweet']
    texts_kotor = texts_kotor.to_list()

    # Sesudah Cleansing
    df['Tweet'] = df['Tweet'].apply(cleansing_data)
    texts = df['Tweet'].to_list()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'text_before_cleansing': texts_kotor,
        'text_after_cleansing' : texts
    }

    kumpulan_kata = list(zip(texts_kotor,texts))

    conn = sqlite3.connect('Database_Challange.db')
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO cleansing (text_ori, text_clean) VALUES (?, ?)", kumpulan_kata)
    
    conn.commit()
    conn.close()

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
	app.run()