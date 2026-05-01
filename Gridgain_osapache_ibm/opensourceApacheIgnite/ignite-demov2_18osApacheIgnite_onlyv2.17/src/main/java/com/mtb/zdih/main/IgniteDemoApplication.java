package com.mtb.zdih.main;

import org.apache.ignite.Ignite;
import org.apache.ignite.IgniteCache;
import org.apache.ignite.cache.CacheAtomicityMode;
import org.apache.ignite.cache.CacheMode;
import org.apache.ignite.cluster.ClusterState;
import org.apache.ignite.configuration.*;
import org.jetbrains.annotations.NotNull;
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
    public ApplicationRunner applicationRunner(Ignite ignite) {
        return args -> {
            IgniteCache<String, String> cache = ignite.getOrCreateCache("dummy");
            //cache.put("key1", "value1");
            //cache.put("tdevyk3", "ykuang@mtb.com");
            System.out.printf("cache.get(\"key1\") = %s, cache.get(\"tdevyk3\") = %s !", cache.get("key1"), cache.get("tdevyk3"));
        };
    }

    @Bean
    public Ignite ignite() {
        IgniteConfiguration cfg = new IgniteConfiguration();
        System.out.printf("IgniteConfiguration newed an instance - %s;\n",cfg.getDiscoverySpi());
        cfg.setDataStorageConfiguration(getDataStorageConfiguration());

        cfg.setCacheConfiguration(getCacheConfiguration());

        Ignite ignite = Ignition.start(cfg);
		ignite.cluster().state(ClusterState.ACTIVE);

        return ignite;
    }

    private CacheConfiguration getCacheConfiguration() {
        CacheConfiguration<String, String> cc = new CacheConfiguration<>();
        cc.setName("dummy");
        cc.setOnheapCacheEnabled(false);
        cc.setBackups(1);
        cc.setCacheMode(CacheMode.REPLICATED);
        cc.setAtomicityMode(CacheAtomicityMode.TRANSACTIONAL);

        return cc;
    }

    private static @NotNull DataStorageConfiguration getDataStorageConfiguration() {
        DataRegionConfiguration drc = new DataRegionConfiguration();
        drc.setName("my-data-region");
        drc.setInitialSize(10 * 1024 * 1024);
        drc.setMaxSize(40 * 1024 * 1024);
        drc.setPageEvictionMode(DataPageEvictionMode.RANDOM_2_LRU);
        Boolean getBooleanIsPersistenceEnabled = drc.isPersistenceEnabled();
        System.out.printf("Is DataRegionConfiguratrion PersistenceEnabled by default? %s;\n",getBooleanIsPersistenceEnabled);
        if (! getBooleanIsPersistenceEnabled) {
            drc.setPersistenceEnabled(true);
            //log.info
            System.out.printf("Set/Changed drc.isPersistenceEnabled() into %s.\n",drc.isPersistenceEnabled());
        }
        DataStorageConfiguration dsc = new DataStorageConfiguration();
        dsc.setDefaultDataRegionConfiguration(drc);

        return dsc;
    }
}
