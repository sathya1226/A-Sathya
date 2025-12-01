package com.example;

import java.util.Scanner;

class Calculator{
    public double add(double a, double b){
        return a + b;
    }

    public double subtract(double a, double b){
        return a - b;
    }

    public double multiply(double a, double b){
        return a * b;
    }

    public double divide(double a, double b){
        if (b == 0){
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return a/b;
    }

    public double calculate(double a, double b, String operationType){
        switch (operationType.toLowerCase()){
            case "add":
                return add(a, b);
            case "sub":
            case "subtract":
                return subtract(a, b);
            case "mul":
            case "multiply":
                return multiply(a, b);
            case "div":
            case "divide":
                return divide(a, b);
            default:
                throw new IllegalArgumentException("Invalid operation type: " + operationType);
        }
    }
}
public class Problem1 {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter a (double): ");
        double a = sc.nextDouble();

        System.out.println("Enter b (double): ");
        double b = sc.nextDouble();

        System.out.print("Enter type of operation (add/sub/mul/div): ");
        String operationType = sc.next();

        Calculator calculator = new Calculator();

        try{
            double result = calculator.calculate(a, b, operationType);
            System.out.println("Result: " + result);
        }catch (Exception e){
            System.out.println("Error: " + e.getMessage());
        }
        sc.close();
    }
}
