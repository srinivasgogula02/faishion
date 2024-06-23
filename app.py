from flask import Flask, render_template, request, redirect, url_for,jsonify
import mysql.connector
from gradio_client import Client, handle_file

client = Client("HumanAIGC/OutfitAnyone")


client2 = Client("stabilityai/stable-diffusion-3-medium")

app = Flask(__name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host='localhost',
#         user='root',
#         password='root',
#         database='fashion_db'
#     )

db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'fashion_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products1 ORDER BY id DESC')
    products1 = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products1)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image_url = request.form['image_url']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, price, image_url) VALUES (%s, %s, %s)',
                       (name, price, image_url))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products1 WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if product is None:
        return "Product not found", 404
    return render_template('product_detail.html', product=product)





@app.route('/try_on', methods=['GET', 'POST'])
def try_on():
    return render_template('try_on.html')

@app.route('/generate_outfit_image', methods=['POST'])
def generate_outfit_image():
    data = request.json
    top_garment_url = data.get('top_garment_url')
    bottom_garment_url = data.get('bottom_garment_url')
    user_image_url = data.get('user_image_url')
    gender = data.get('gender')
    print(gender)
    print(user_image_url)
    print(top_garment_url)
    print(bottom_garment_url)
    
    if gender == 'female':
        model_url = 'https://humanaigc-outfitanyone.hf.space/file=/tmp/gradio/28dbd2deba1e160bfadffbc3675ba4dcac20ca58/Eva_0.png'
    else :
        model_url = 'https://humanaigc-outfitanyone.hf.space/file=/tmp/gradio/6f793bb1d75f34cdc2c980467ef2f2c242fe9b56/Yifeng_0.png'
    
    result = client.predict(
		model_name=handle_file(model_url),
		garment1=handle_file(top_garment_url),
		garment2=handle_file(bottom_garment_url),
		api_name="/get_tryon_result"

)

    # Simulate image generation logic
    generated_image_url = result # This should be the generated image URL
    return jsonify({'image_url': 'https://humanaigc-outfitanyone.hf.space/file='+generated_image_url})


@app.route('/add_to_community', methods=['GET', 'POST'])
def add_to_community():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        top_garment_url = request.form.get('top_garment_url')
        top_garment_price = request.form.get('top_garment_price')
        top_garment_image_url = request.form.get('top_garment_image_url')
        
        bottom_garment_url = request.form.get('bottom_garment_url')
        bottom_garment_price = request.form.get('bottom_garment_price')
        bottom_garment_image_url = request.form.get('bottom_garment_image_url')
        
        outfit_image_url = request.form.get('outfit_image_url')

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products1 (title, description, top_garment_url, top_garment_price, top_garment_image_url, bottom_garment_url, bottom_garment_price, bottom_garment_image_url, outfit_image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                title,
                description,
                top_garment_url,
                top_garment_price,
                top_garment_image_url,
                bottom_garment_url,
                bottom_garment_price,
                bottom_garment_image_url,
                outfit_image_url
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

    return render_template('add_to_community.html')



# Route to render the "Create" page
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        input_text = request.json['input_text']
        generated_image_url = generate_image(input_text)  # Replace this with your actual image generation logic
        return jsonify({'image_url': generated_image_url})
    else:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM create1")
        created_items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('create.html', created_items=created_items)

# Route to add the generated image to the community
@app.route('/add_to_communit2', methods=['POST'])
def add_to_community2():
    data = request.json
    input_text = data['input_text']
    image_url = data['image_url']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO create1 (input_text, image_url) VALUES (%s, %s)", (input_text, image_url))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

def generate_image(input_text):
    result = client.predict(
		prompt=input_text,
		negative_prompt="Hello!!",
		seed=0,
		randomize_seed=True,
		width=1024,
		height=1024,
		guidance_scale=5,
		num_inference_steps=28,
		api_name="/infer"
)
    # Placeholder function for image generation
    return f'https://stabilityai-stable-diffusion-3-medium.hf.space{result}'



if __name__ == '__main__':
    app.run(debug=True)

