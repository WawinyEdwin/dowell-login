def api(word):
    if not word or len(word) == 0 or re.search('[a-zA-Z]', word):
        return {
                "message": "String is empty or invalid",
                "success": False,
                "input_string": word
            }
    try:
        detector = google_translator()

        return_data = list()
        language_list = []
        
        for item in word.split(' '):
            detect_result = detector.detect(item)
            return_data.append(
                {
                    "input_string": item,
                    "short_form": detect_result[0],
                    "long_form": detect_result[1]
                }
            )
            language_list.append(detect_result[0])

        return {
            "data": return_data,
            "success": True,
            "input_string": word,
            "same_language": len(set(language_list)) == 1
        }
    except Exception as e:
        print(e)
        return {
            "message": "String is empty or invalid",
            "success": False
        }

# api(english)
