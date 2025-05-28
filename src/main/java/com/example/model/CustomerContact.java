package com.example.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "customer_contact")
public class CustomerContact {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "PROFILE_ID")
    private String profileId;

    @Column(name = "TENANT_ID")
    private String tenantId;

    @Column(name = "CONTACT_TYPE")
    private String contactType;  // MOB, TEL, EML, FAX

    @Column(name = "CONTACT_VALUE")
    private String contactValue;

    @Column(name = "PREFERRED_FLAG")
    private String preferredFlag;  // Y, N

    @Column(name = "CONTACT_STATUS")
    private String contactStatus;  // ACTIVE, INACTIVE

    @Column(name = "MAKER_ID")
    private String makerId;

    @Column(name = "CHECKER_ID")
    private String checkerId;

    @Column(name = "MAKER_TIMESTAMP")
    private LocalDateTime makerTimestamp;

    @Column(name = "CHECKER_TIMESTAMP")
    private LocalDateTime checkerTimestamp;
} 