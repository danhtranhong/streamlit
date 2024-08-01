
import ultralytics
from ultralytics import YOLO
from ultralytics import settings
import mlflow
import os
import pandas as pd
import yaml as yaml
import matplotlib.pyplot as plt
import shutil
from PIL import Image


# batch_size = 12
# epochs = 20
# learning_rate = 0.01


mlflow.search_experiments()
settings.update({"mlflow": True})
mlflow.set_tracking_uri(uri="http://localhost:5000")

mlflow.set_experiment("waste-detection2")
#dataset = mlflow.data.from_numpy(array, source="data.csv")

# Get the absolute path of your current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to your training results
training_results_dir = os.path.join(script_dir, "..", "waste-detection", "training_results", "train_12batch_20epochs")

with mlflow.start_run() as run:
    settings.update({"mlflow": True})
    result_metrics = pd.read_csv("D:\\Data_Analytics\streamlit\waste-detection\\training_results\\train_12batch_20epochs\\results.csv")
# >>> result_metrics.columns.tolist()
# ['                  epoch',
# '         train/box_loss',
# '         train/cls_loss',
# '         train/dfl_loss',
# '   metrics/precision(B)',
# '      metrics/recall(B)',
# '       metrics/mAP50(B)',
# '    metrics/mAP50-95(B)',
# '           val/box_loss',
# '           val/cls_loss',
# '           val/dfl_loss',
# '                 lr/pg0',
# '                 lr/pg1',
# '                 lr/pg2']
    best_train_box_loss = result_metrics['         train/box_loss'].max()
    best_train_cls_loss = result_metrics['         train/cls_loss'].max()
    # Metrics
    mlflow.log_metric("best_train_box_loss", best_train_box_loss)
    mlflow.log_metric("best_train_cls_loss", best_train_cls_loss)

    for epoch in result_metrics['                  epoch']:
        train_cls_loss = result_metrics[result_metrics['                  epoch'] == epoch]['         train/cls_loss'].iloc[0]
        train_box_loss = result_metrics[result_metrics['                  epoch'] == epoch]['         train/box_loss'].iloc[0]
        train_dfl_loss = result_metrics[result_metrics['                  epoch'] == epoch]['         train/dfl_loss'].iloc[0]
        precisionB = result_metrics[result_metrics['                  epoch'] == epoch]['   metrics/precision(B)'].iloc[0]
        recallB = result_metrics[result_metrics['                  epoch'] == epoch]['      metrics/recall(B)'].iloc[0]
        mAP50B = result_metrics[result_metrics['                  epoch'] == epoch]['       metrics/mAP50(B)'].iloc[0]
        mAP50_95B = result_metrics[result_metrics['                  epoch'] == epoch]['    metrics/mAP50-95(B)'].iloc[0]

        val_cls_loss = result_metrics[result_metrics['                  epoch'] == epoch]['           val/cls_loss'].iloc[0]
        val_box_loss = result_metrics[result_metrics['                  epoch'] == epoch]['           val/box_loss'].iloc[0]
        val_dfl_loss = result_metrics[result_metrics['                  epoch'] == epoch]['           val/dfl_loss'].iloc[0]

        lr_pg0 = result_metrics[result_metrics['                  epoch'] == epoch]['                 lr/pg0'].iloc[0]
        lr_pg1 = result_metrics[result_metrics['                  epoch'] == epoch]['                 lr/pg1'].iloc[0]
        lr_pg2 = result_metrics[result_metrics['                  epoch'] == epoch]['                 lr/pg2'].iloc[0]

        mlflow.log_metric("train/cls_loss", train_cls_loss, step=epoch)
        mlflow.log_metric("train/box_loss", train_box_loss, step=epoch)
        mlflow.log_metric("train/dfl_loss", train_dfl_loss, step=epoch)

        mlflow.log_metric("metrics/precisionB", precisionB, step=epoch)
        mlflow.log_metric("metrics/recallB", recallB, step=epoch)
        mlflow.log_metric("metrics/mAP50B", mAP50B, step=epoch)
        mlflow.log_metric("metrics/mAP50-95B", mAP50_95B, step=epoch)

        mlflow.log_metric("val/cls_loss", val_cls_loss, step=epoch)
        mlflow.log_metric("val/box_loss", val_box_loss, step=epoch)
        mlflow.log_metric("val/dfl_loss", val_dfl_loss, step=epoch)

        mlflow.log_metric("lr/pg0", lr_pg0, step=epoch)
        mlflow.log_metric("lr/pg1", lr_pg1, step=epoch)
        mlflow.log_metric("lr/pg2", lr_pg2, step=epoch)




    # Parameters
    with open("waste-detection/training_results/train_12batch_20epochs/args.yaml", "r") as f:
        args = yaml.safe_load(f)
    learning_rate = args["lr0"]
    batch_size = args["batch"]
    box = args["box"]
    dfl = args["dfl"]
    epochs = args["epochs"]
    patience = args["patience"]
    imgsz = args["imgsz"]
    workers = args["workers"]
    final_learning_rate = args["lrf"]
    momentum = args["momentum"]
    weight_decay = args["weight_decay"]
    warmup_epochs = args["warmup_epochs"]
    warmup_momentum = args["warmup_momentum"]
    warmup_bias_lr = args["warmup_bias_lr"]
    # Log model parameters
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("box", box)
    mlflow.log_param("dfl", dfl)
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("img_size", imgsz)
    mlflow.log_param("learning_rate", learning_rate)
    mlflow.log_param("learning_rate", final_learning_rate)
    mlflow.log_param("patience", patience)
    mlflow.log_param("momentum", momentum)
    mlflow.log_param("weight_decay", weight_decay)
    mlflow.log_param("warmup_epochs", warmup_epochs)
    mlflow.log_param("warmup_momentum", warmup_momentum)
    mlflow.log_param("warmup_bias_lr", warmup_bias_lr)
    mlflow.log_param("workers", workers)


    # Log artifact
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/weights/best.pt", artifact_path="model")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/weights/last.pt",artifact_path="model")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/labels.jpg", artifact_path="labels")

    # Log artifact Trainign result
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/args.yaml", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/confusion_matrix.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/confusion_matrix_normalized.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/F1_curve.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/labels.jpg", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/labels_correlogram.jpg", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/PR_curve.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/P_curve.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/results.csv", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/results.png", artifact_path="training_results")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/R_curve.png", artifact_path="training_results")

    # Log artifact training-batch
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch0.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch1.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch2.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch20.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch21.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/train_batch22.jpg", artifact_path="train-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/val_batch0_pred.jpg", artifact_path="val-batch-result")
    mlflow.log_artifact("waste-detection/training_results/train_12batch_20epochs/val_batch0_labels.jpg", artifact_path="val-batch-result")