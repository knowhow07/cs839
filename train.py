import tensorflow as tf
import numpy as np
import pandas as pd
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "5" 
train_df = pd.read_parquet('train_data.parquet', engine='pyarrow')
train_df.info()
test_df = pd.read_parquet('test_data.parquet', engine='pyarrow')
test_df.info()
validation_df = pd.read_parquet('validation_data.parquet', engine='pyarrow')
validation_df.info()
# Create a TensorFlow Dataset
def df_to_tfdata(df, batch_size=16):
    dataset = tf.data.Dataset.from_tensor_slices((
        {
            'input_ids': list(df['input_ids']),
            'attention_mask': list(df['attention_mask'])
        },
        list(df['numeric_labels'])
    ))
    dataset = dataset.batch(batch_size)
    return dataset

train_dataset = df_to_tfdata(train_df)  # Adjust batch_size if needed
validation_dataset = df_to_tfdata(validation_df)
test_dataset = df_to_tfdata(test_df)

print("TensorFlow dataset created")

from transformers import TFBertForTokenClassification, BertTokenizerFast

# Use the legacy Adam optimizer as recommended for M1/M2 Macs
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
model = TFBertForTokenClassification.from_pretrained('bert-base-uncased',
                                                      num_labels=15)  # Adjust num_labels to match your dataset

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
# Use the legacy Adam optimizer as recommended for M1/M2 Macs
# optimizer = tf.keras.optimizers.legacy.Adam(learning_rate=5e-5)
loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
model.compile(optimizer=optimizer, loss=loss, metrics=[metric])

print("Model created")

tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="./logs")
early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)

model_history = model.fit(
    train_dataset,
    epochs=3,
    callbacks=[tensorboard_callback, early_stopping_callback]
)

# validation_loss, validation_accuracy = model.evaluate(validation_dataset)
# print(f"Validation Loss: {validation_loss}")
# print(f"Validation Accuracy: {validation_accuracy}")

# test_loss, test_accuracy = model.evaluate(test_dataset)
# print(f"Test Loss: {test_loss}")
# print(f"Test Accuracy: {test_accuracy}")

model.save_pretrained("my_pii_detection_model")
tokenizer.save_pretrained("my_pii_detection_model")

print("Model saved")