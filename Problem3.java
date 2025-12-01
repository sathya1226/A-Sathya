package com.example;

import java.util.Scanner;

public class Problem3 {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter a (integer): ");
        int a = sc.nextInt();

        if (a <= 0){
            System.out.println("Please enter a positive integer");
            sc.close();
            return;
        }

        int count;
        if (a % 2 == 0){
            count = a - 1;
        }else {
            count = a;
        }

        StringBuilder result = new StringBuilder();

        for (int i = 1; i <= count; i++){
            int value = 2 * i - 1;
            result.append(value);
            if (i < count){
                result.append(", ");
            }
        }

        System.out.println("Output: " + result.toString());
        sc.close();
    }
}
