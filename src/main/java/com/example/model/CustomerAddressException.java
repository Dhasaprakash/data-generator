package com.example.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "customer_address_exception")
public class CustomerAddressException {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ADDRESS_ID")
    private Long addressId;

    @Column(name = "TENANT_ID")
    private String tenantId;

    @Column(name = "PROFILE_ID")
    private String profileId;

    @Column(name = "ADDRESS_TYPE")
    private String addressType;

    @Column(name = "EXCEPTION_TYPE")
    private String exceptionType;  // ADDRESS_MISMATCH, INVALID_POSTCODE, UNDELIVERABLE

    @Column(name = "EXCEPTION_STATUS")
    private String exceptionStatus;  // OPEN, CLOSED, IN_PROGRESS

    @Column(name = "EXCEPTION_DESCRIPTION")
    private String exceptionDescription;

    @Column(name = "RESOLUTION_CODE")
    private String resolutionCode;  // CORRECTED, VERIFIED, PENDING, NA

    @Column(name = "MAKER_ID")
    private String makerId;

    @Column(name = "CHECKER_ID")
    private String checkerId;

    @Column(name = "MAKER_TIMESTAMP")
    private LocalDateTime makerTimestamp;

    @Column(name = "CHECKER_TIMESTAMP")
    private LocalDateTime checkerTimestamp;
} 