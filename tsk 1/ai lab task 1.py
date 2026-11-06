
def scholarship(score, documents, eligibility, recommendation):
    print("Scholarship Application Details")
    print("Score:", score)
    print("Documents Complete:", documents)
    print("Eligibility Confirmed:", eligibility)
    print("Recommendation Submitted:", recommendation)
    if score >= 70 and documents == True and eligibility == True and recommendation == True:
        print("Result: Review")
        print("Reason: All conditions are satisfied.")
    else:
        print("Result: Hold")
        print("Reason: One or more conditions are not satisfied.")
    print("-----------------------------")
scholarship(82, True, True, True)
scholarship(82, True, False, True)
scholarship(82, True, True, False)
scholarship(70, True, True, True)