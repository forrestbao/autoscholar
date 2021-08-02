import config as cfg
import json
import os
from model import *
from main import process_file
import sklearn

def main():
    tsvs = os.listdir(cfg.dataset_folder)
    scores = {}
    for leave_one in tsvs:
        print(leave_one)
        with open(cfg.train_tsv_file, "w", encoding="utf-8") as writer:
            for other in tsvs:
                if other == leave_one:
                    continue
                with open(os.path.join(cfg.dataset_folder, other), "r", encoding="utf-8") as f:
                    writer.write(f.read())
        
        model = SVM()
        model.preprocessing(cfg.train_tsv_file)
        save_model(model, cfg.model_file)
        # Reload
        model = load_model(cfg.model_file)
        model.train(grid_search=False)
        # save_model(model, cfg.model_file)

        # Calculate PR
        labels, texts = [], []
        with open(os.path.join(cfg.dataset_folder, leave_one), 'r') as f: 
            for Line in f:
                if len(Line) > 5: 
                    labels.append(int(Line[0]))
                    texts.append(Line[1:].strip())
        
        predicts = model.predict(texts)
        scores[leave_one] = (sklearn.metrics.precision_score(labels, predicts), sklearn.metrics.recall_score(labels, predicts))

        # Generate Output
        pdf_name = ".".join(leave_one.split(".")[:-1])
        pdf_file = os.path.join(cfg.input_folder, pdf_name)
        output_file = os.path.join(cfg.output_folder, pdf_name)
        process_file(model, pdf_file, output_file)
    
    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

if __name__ == "__main__":
    main()