package com.example;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Scanner;

public class Problem4 {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter number of elements");
        int n = sc.nextInt();

        int[] numbers = new int[n];
        System.out.println("Enter " + n + " integers:");
        for (int  i = 0; i < n; i++){
            numbers[i] = sc.nextInt();
        }

        Map<Integer, Integer> result = getMultipleCount(numbers);

        System.out.println("Input: " + Arrays.toString(numbers));
        System.out.println("Output: " + result);
        sc.close();
    }

    private static Map<Integer, Integer> getMultipleCount(int[] numbers){
        Map<Integer, Integer> countMap = new LinkedHashMap<>();

        for (int k = 1; k <= 9; k++){
            int count = 0;
            for (int num : numbers){
                if(num % k == 0){
                    count++;
                }
            }
            countMap.put(k, count);
        }
        return countMap;
    }
}
