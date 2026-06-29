package com.devforge.springboot.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class InfoController {

    @GetMapping("/info")
    public Map<String, Object> getInfo() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Welcome to DevForge Spring Boot Platform");
        response.put("status", "operational");
        response.put("javaVersion", System.getProperty("java.version"));
        response.put("databasesAvailable", new String[]{"PostgreSQL", "MongoDB", "Redis", "Neo4j"});
        return response;
    }
}
