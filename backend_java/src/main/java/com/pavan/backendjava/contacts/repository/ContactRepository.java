package com.pavan.backendjava.contacts.repository;

import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.pavan.backendjava.contacts.domain.Contact;

public interface ContactRepository extends MongoRepository<Contact, String> {

    Optional<Contact> findByEmailIgnoreCase(String email);
}
