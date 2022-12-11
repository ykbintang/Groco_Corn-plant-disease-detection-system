from flask import Flask, render_template, Flask, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from time import sleep
import numpy as np
import os
from flask_session import Session
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.models import load_model
from keras.models import model_from_json
from keras.utils import load_img
from keras.utils import img_to_array

MODELS_ARCHITECTURE = 'models/model_corn_disease_1.json'
MODELS_WEIGHT = 'models/model_corn_disease_weight.h5'

json_file = open(MODELS_ARCHITECTURE)
loaded_model_json = json_file.read()
json_file.close()

models = model_from_json(loaded_model_json)
models.load_weights(MODELS_WEIGHT)

print('@@ Model loaded. Check http://127.0.0.1:5000/')


def predict(img_path, models):
    test_image = load_img(img_path, target_size=(224, 224))
    print('@@ Got Image for prediction')

    test_image = img_to_array(test_image) / 255
    test_image = np.expand_dims(test_image, axis=0)

    result = models.predict(test_image)
    print(result[0])
    classes = np.argmax(np.around(result[0]), axis=0)
    return classes


app = Flask(__name__, template_folder='web')
app.secret_key = 'algo908%jejeneverdiesiapajejesayagatau'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

KONDISI = ['BLIGHT', 'COMMON RUST', 'GRAY LEAF SPOT', 'HEALTHY']
TIPS1 = [
    'Strategi manajemen preventif dapat mengurangi kerugian ekonomi dari NCLB. Manajemen pencegahan sangat penting untuk bidang yang berisiko tinggi untuk perkembangan penyakit. Pilihan pengelolaan penyakit dalam musim, seperti fungisida, juga tersedia.',
    'Penyakit ini menyukai suhu dingin (60 - 76 derajat F), embun yang lebat, sekitar enam jam kebasahan daun, dan kelembapan relatif lebih dari 95 persen. Suhu di atas 80 derajat F menekan perkembangan dan penyebaran penyakit.',
    'Patogennya adalah jamur yang disebut Cercospora zeae-maydis. Satu-satunya inang yang diketahui adalah jagung dan melewati musim dingin di puing-puing di permukaan tanah.',
    'Waaahh.. Selamat tanaman jagung Anda SEHAT.'
]
TIPS2 = [
    'Resistensi utama (vertikal) hibrida jagung berasal dari gen spesifik ras Ht1, Ht2, Ht3, dan HtN, dengan gen Ht1 yang paling umum. Tanaman dengan gen Ht1 Ht2, atau Ht3 memiliki lesi klorotik yang lebih kecil dan sporulasi yang berkurang.[2] Gen HtN menunda gejala sampai setelah serbuk sari ditumpahkan. Secara individual, masing-masing gen Ht memiliki efektivitas terbatas karena ada ras E',
    'Praktik manajemen terbaik adalah dengan menggunakan jagung hibrida tahan. Fungisida juga bisa bermanfaat, terutama jika diterapkan lebih awal ketika beberapa pustula muncul di daun.',
    'Taktik pengelolaan penyakit termasuk menggunakan jagung hibrida yang tahan, pengolahan tanah konvensional jika sesuai, dan rotasi tanaman. Fungisida daun bisa efektif jika dijamin secara ekonomi. Biasanya mereka hanya menguntungkan pada inbrida rentan atau hibrida rentan di bawah kombinasi kondisi berisiko tinggi dengan potensi hasil tinggi, kondisi lembab berkepanjangan, dan bukti perkembangan penyakit.',
    'Tetap terus rawat tanaman Anda agar selalu terhindar dari penyakit yaa! Kenali gejala penyakit yang dapat menyerang tanaman jagung Anda juga, agar ketika tanaman jagung Anda terkena penyakit Anda bisa mengatasinya dengan cepat. Pantau juga tanaman Anda dari serangan hama agar tanaman Anda tetap sehat sampai masa panen tiba. Good Luck :)'
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload():
    sleep(2)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            classes = predict(filepath, models)
            session['classes'] = str(classes)
            session['filepath'] = filepath
            return redirect(url_for('hasil'))


@app.route('/dokumentasi')
def dokumentasi():
    return render_template('dokumentasi.html')


@app.route('/tentang')
def tentang():
    return render_template('tentang.html')


@app.route('/hasil')
def hasil():
    classes = int(session.get('classes'))
    filepath = session.get('filepath')
    return render_template('hasil.html',
                            penyakit=KONDISI[classes],
                            imagepath=filepath,
                            tips1=TIPS1[classes],
                            tips2=TIPS2[classes])


@app.route('/upload')
def proses():
    return render_template('proses.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
