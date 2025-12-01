package com.example;

import java.util.Scanner;

public class Problem2 {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter a (integer): ");
        int a = sc.nextInt();

        if (a <= 0){
            System.out.println("Please enter a positive integer");
            sc.close();
            return;
        }
        
        StringBuilder result = new StringBuilder();

        for (int i = 1; i <= a; i++){
            int value = 2 * i - 1;
            result.append(value);
            if (i < a){
                result.append(", ");
            }
        }

        System.out.println("Output: " + result.toString());
        sc.close();
    }
}
