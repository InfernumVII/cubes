
from flask import Flask, render_template, request
app = Flask(__name__)
class mainFuncs:
    def __init__(self, value):
        self.value = value
        self.hex_value = self.decimal_to_hex(value)
        self.have_minus = value < 0


        self.hex_map = {
            '0': '0000',
            '1': '0001',
            '2': '0010',
            '3': '0011',
            '4': '0100',
            '5': '0101',
            '6': '0110',
            '7': '0111',
            '8': '1000',
            '9': '1001',
            'A': '1010',
            'B': '1011',
            'C': '1100',
            'D': '1101',
            'E': '1110',
            'F': '1111'
        }

    def increment_hex(self, hex_string):
        """Helper function to increment a hexadecimal integer string."""
        carry = 1
        hex_list = list(hex_string)
        for i in range(len(hex_list) - 1, -1, -1):
            digit = int(hex_list[i], 16) + carry
            if digit < 16:
                hex_list[i] = hex(digit)[-1].upper()
                carry = 0
                break
            else:
                hex_list[i] = '0'
                carry = 1
        if carry == 1:
            hex_list.insert(0, '1')
        return ''.join(hex_list)
    def decimal_to_hex(self, value):
        def custom_len(hex_frac):
            return len(hex_frac.lstrip("0"))

        value = abs(value)
        
        # Split the value into integer and fractional parts
        integer_part = int(value)
        fractional_part = value - integer_part
        
        # Convert the integer part to hexadecimal
        hex_int = ""
        while integer_part > 0:
            remainder = integer_part % 16
            if remainder < 10:
                hex_int = str(remainder) + hex_int
            else:
                hex_int = chr(55 + remainder) + hex_int  # 55 + 10 = 'A', 55 + 15 = 'F'
            integer_part //= 16
        
        if hex_int == "":
            hex_int = "0"
        
        # Convert the fractional part to hexadecimal
        hex_frac = ""
        precision = 7  # Calculate up to 7 characters
        while fractional_part > 0 and custom_len(hex_frac) < precision:
            fractional_part *= 16
            digit = int(fractional_part)
            if digit < 10:
                hex_frac += str(digit)
            else:
                hex_frac += chr(55 + digit)
            fractional_part -= digit
        
        # Round the fractional part if the 7th digit exists
        if custom_len(hex_frac) == 7:
            if int(hex_frac[-1], 16) >= 8:  # Check if the 7th digit >= 8
                # Increment the 6th digit
                carry = 1
                hex_frac = list(hex_frac[:-1])  # Remove the 7th digit
                for i in range(len(hex_frac) - 1, -1, -1):
                    digit = int(hex_frac[i], 16) + carry
                    if digit < 16:
                        hex_frac[i] = hex(digit)[-1].upper()
                        carry = 0
                        break
                    else:
                        hex_frac[i] = '0'
                        carry = 1
                if carry == 1:
                    hex_int = self.increment_hex(hex_int)
            else:
                hex_frac = hex_frac[:-1]  # Truncate the 7th digit
        
        hex_frac = ''.join(hex_frac)
        
        # Combine integer and fractional parts
        if hex_frac:
            return f"{hex_int}.{hex_frac}"
        return f"{hex_int}"
    

    def HexToBin(self, mantissa):
        if '.' in mantissa:

            splitted = mantissa.split('.')[1]
        else:
            splitted = list(mantissa)
        return ''.join(self.hex_map[i] for i in splitted)
    def calculate_characteristic(self, P, BIAS, c):
        """
        Вычисляет характеристику числа с учётом порядка и смещения.
        
        :param P: Порядок числа (целое число, может быть отрицательным)
        :return: Характеристика числа в виде строки двоичного числа
        """
        # Смещение (bias)

        XB = P + BIAS  
        characteristic = f"{XB:0{c}b}"
        return characteristic
    def calcEXP(self, value):
        if '.' not in value:
            # Если число не содержит точки, добавляем ее в конец и возвращаем порядок и мантиссу
            return len(value), f"0.{value}"
        else:
            # Разделяем на целую и дробную часть
            splitted = value.split('.')
            integer_part = splitted[0]
            fractional_part = splitted[1]

            # Если целая часть равна 0
            if integer_part == '0':
                # Считаем, на сколько цифр в дробной части нужно сдвинуть запятую
                shift = 0
                for char in fractional_part:
                    if char != '0':
                        break
                    shift += 1
                # Возвращаем отрицательный порядок (сдвиг влево) и нормализованную мантиссу
                mantissa = f"0.{fractional_part[shift:]}"
                return -shift, mantissa

            else:
                # Если целая часть не равна 0
                shift = len(integer_part)
                # Формируем мантиссу и возвращаем порядок
                mantissa = f"{integer_part[0]}.{integer_part[1:]}{fractional_part}"
                return shift - 1, mantissa
    def improveMantisa(self, binned, c):
        return binned.ljust(c, "0")
    
class F1(mainFuncs):
    def __init__(self, value):
        super().__init__(value)
        self.BIAS = 64
        self.shift, self.mantissa = self.calcEXP(self.hex_value)
        self.characteristic = self.calculate_characteristic(self.shift, self.BIAS, 7)
        self.binhex = self.HexToBin(self.mantissa)
        self.improvedMantisa = self.improveMantisa(self.binhex, 24)
    
    
    
    def __repr__(self) -> str:
        groups = [1, 3, 4, 4, 4, 4, 4, 4, 4]
        s = f"{int(self.have_minus)}{self.characteristic}{self.improvedMantisa}"
        splitted = []
        index = 0
        for group in groups:
            splitted.append(s[index:index+group])
            index += group
        splitted = ' '.join(splitted)
        splitted = splitted[:1] + '|' + splitted[2:10] + '|' + splitted[11:]
        minus = '-' if self.have_minus else ''
        output = f"""
            A = {minus}({abs(self.value)})₁₀={minus}({self.hex_value})₁₆ * 16^{self.shift},

            X = P + {self.BIAS} = ({self.shift + self.BIAS})₁₀ = ({self.characteristic})₂",

            {splitted}
        """
        return output
class F2(mainFuncs):
    def __init__(self, value):
        super().__init__(value)
        self.BIAS = 128
        self.binhex = self.HexToBin(self.hex_value)
        self.shift, self.mantissa = self.calcEXP(self.binhex)
        self.characteristic = self.calculate_characteristic(self.shift, self.BIAS, 8)
        self.improvedMantisa = self.improveMantisa(self.mantissa, 26)

    def HexToBin(self, mantissa):
        if '.' in mantissa:
            splitted = mantissa.split('.')
            return f"{splitted[0]}.{''.join(self.hex_map[i] for i in splitted[1])}"
        else:
            return ''.join(self.hex_map[i] for i in mantissa).lstrip('0')
        return ''.join(self.hex_map[i] for i in splitted)
    def __repr__(self) -> str:
        groups = [1, 4, 4, 4, 4, 4, 4, 4, 4]
        s = f"{int(self.have_minus)}{self.characteristic}{self.improvedMantisa[2:]}"
        splitted = []
        index = 0
        for group in groups:
            splitted.append(s[index:index+group])
            index += group
        splitted = ' '.join(splitted)
        splitted = splitted[:1] + '|' + splitted[2:11] + '|' + splitted[13:]
        minus = '-' if self.have_minus else ''
        output = f"""
            A = {minus}({abs(self.value)})₁₀ ={minus}({self.hex_value})₁₆ ={minus}({self.binhex})₂ = {minus}({self.mantissa.rstrip('0')})₂ * 2^{self.shift},

            X = P + {self.BIAS} = ({self.shift + self.BIAS})₁₀ = ({self.characteristic})₂,

            {splitted}
        """
        return output
class F3(mainFuncs):
    def __init__(self, value):
        super().__init__(value)
        self.BIAS = 127
        self.binhex = self.HexToBin(self.hex_value)
        self.shift, self.mantissa = self.calcEXP(self.binhex)
        self.shift -= 1
        self.characteristic = self.calculate_characteristic(self.shift, self.BIAS, 8)
        self.improvedMantisa = self.improveMantisa(self.mantissa, 26)

    def HexToBin(self, mantissa):
        if '.' in mantissa:
            splitted = mantissa.split('.')
            return f"{splitted[0]}.{''.join(self.hex_map[i] for i in splitted[1])}"
        else:
            return ''.join(self.hex_map[i] for i in mantissa).lstrip('0')
        return ''.join(self.hex_map[i] for i in splitted)
    def __repr__(self) -> str:
        groups = [1, 4, 3, 4, 4, 4, 4, 4, 5]
        s = f"{int(self.have_minus)}{self.characteristic}{self.improvedMantisa[2:]}"
        splitted = []
        index = 0
        for group in groups:
            splitted.append(s[index:index+group])
            index += group
        splitted = ' '.join(splitted)
        splitted = splitted[:1] + '|' + splitted[2:11] + '|' + splitted[13:]
        minus = '-' if self.have_minus else ''
        output = f"""
            A = {minus}({abs(self.value)})₁₀ ={minus}({self.hex_value})₁₆ ={minus}({self.binhex})₂ = {minus}({self.mantissa.rstrip('0')})₂ * 2^{self.shift},

            X = P + {self.BIAS} = ({self.shift + self.BIAS})₁₀ = ({self.characteristic})₂,

            {splitted}
        """
        return output
TESTS = [
    250, 
    0.0025,
    1825,
    0.76,
    850,
    0.105
]

# Test the function
for i in TESTS:
    F1new = F3(i)
    print(F1new)
    #print(F1new.mantissa)
    #print(F1new.value)
    #print(F1new.hex_value)
    #print(F1new.shift)
    #print(len(F1new.characteristic))
    #print(F1new.mantissa)
    #print(len(F1new.improvedMantisa))


    #print(int(F1new.have_minus), F1new.characteristic, F1new.improvedMantisa)
    print('----------------')
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            value = request.form['value']
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
            selected_class = request.form['class']
            if selected_class == 'F1':
                instance = F1(value)
            elif selected_class == 'F2':
                instance = F2(value)
            elif selected_class == 'F3':
                instance = F3(value)
            result = repr(instance)
        except ValueError:
            result = 'Ошибка: Пожалуйста, введите корректное число.'

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
