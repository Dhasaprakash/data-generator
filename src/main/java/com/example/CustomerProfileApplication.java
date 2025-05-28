package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

@EnableKafka
@SpringBootApplication
public class CustomerProfileApplication {
    public static void main(String[] args) {
        SpringApplication.run(CustomerProfileApplication.class, args);
    }
} 