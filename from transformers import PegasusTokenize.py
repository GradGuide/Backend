from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# تحميل النموذج والمحول (Tokenizer)
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

def summarize_text(text):
    # تحويل النص إلى توكنز
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)

    # توليد التلخيص
    summary_ids = model.generate(**inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4)
    
    # فك ترميز التلخيص
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

# تجربة تلخيص نص
text = """
الذكاء الاصطناعي هو أحد أكثر المجالات التقنية تطورًا في الوقت الحالي، حيث يتم استخدامه في مختلف الصناعات 
مثل الرعاية الصحية، والتكنولوجيا المالية، والتعليم. يعتمد الذكاء الاصطناعي على تحليل البيانات والتعلم العميق
لتقديم توقعات دقيقة وحلول فعالة.
"""
summary = summarize_text(text)
print("🔹 النص الأصلي:\n", text)
print("\n🔹 التلخيص:\n", summary)
