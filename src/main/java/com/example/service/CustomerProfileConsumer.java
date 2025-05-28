package com.example.service;

import com.example.model.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import jakarta.persistence.EntityManager;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class CustomerProfileConsumer {

    private final EntityManager entityManager;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = "${kafka.topic.customer-profiles}", groupId = "${spring.kafka.consumer.group-id}")
    @Transactional
    public void consume(Map<String, Object> message) {
        try {
            log.info("Received customer profile message: {}", message);
            
            // Convert the message to CustomerProfile
            CustomerProfile profile = objectMapper.convertValue(message, CustomerProfile.class);
            
            // Save the customer profile
            entityManager.persist(profile);
            
            log.info("Successfully processed and saved customer profile with ID: {}", profile.getProfileId());
        } catch (Exception e) {
            log.error("Error processing customer profile message: {}", e.getMessage(), e);
            throw e;
        }
    }
} 