package com.example.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.List;

@Data
@Entity
@Table(name = "customer_profile")
public class CustomerProfile {
    @Id
    @Column(name = "PROFILE_ID")
    private String profileId;
    
    @Column(name = "TENANT_ID")
    private String tenantId;

    @Column(name = "PROFILE_TYPE")
    private String profileType;  // I, S

    @Column(name = "PROFILE_STATUS")
    private String profileStatus;  // ACTIVE, INACTIVE, DELETED

    @Column(name = "RELATIONSHIP_NUMBER")
    private String relationshipNumber;

    @Column(name = "FIRST_NAME")
    private String firstName;

    @Column(name = "MIDDLE_NAME")
    private String middleName;

    @Column(name = "LAST_NAME")
    private String lastName;

    @Column(name = "FULL_NAME")
    private String fullName;

    @OneToMany(cascade = CascadeType.ALL)
    @JoinColumn(name = "PROFILE_ID")
    private List<CustomerAddress> addresses;

    @OneToMany(cascade = CascadeType.ALL)
    @JoinColumn(name = "PROFILE_ID")
    private List<CustomerContact> contacts;

    @OneToMany(cascade = CascadeType.ALL)
    @JoinColumn(name = "PROFILE_ID")
    private List<CustomerDueDiligence> customerDueDiligence;
} 