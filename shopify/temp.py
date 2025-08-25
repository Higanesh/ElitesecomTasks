
def lengthOfLastWord(s):
        temp = s.split()
        print(temp)
        result = " ".join(temp)
        print(result)
        for i in range(-1,len(s)):
            if result[i] == " ":
                return i
            
        return len(result)

print(lengthOfLastWord("   fly me   to   the moon  "))  # Output: 5