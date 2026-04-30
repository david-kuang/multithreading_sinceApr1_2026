package com.mtb.zdih.main;

import org.apache.ignite.Ignite;
import org.apache.ignite.IgniteCache;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.apache.ignite.Ignition;

@SpringBootApplication
public class IgniteDemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(IgniteDemoApplication.class, args);
	}

	@Bean
	public ApplicationRunner applicationRunner() {
		return args -> {
			Ignite ignite = Ignition.start();

			IgniteCache<String, String> cache = ignite.getOrCreateCache("dummy");
			cache.put("key1","value1");

			System.out.println(cache.get("key1"));
		};
	}

}
