import joblib

def load_model():
    return joblib.load("mlp_face_model.pkl")

def predict_user_identity(model, image_array):
    pred = model.predict([image_array])
    print("Predicted label ",pred)
    return pred[0]  # Assuming your model returns the CNE as string
