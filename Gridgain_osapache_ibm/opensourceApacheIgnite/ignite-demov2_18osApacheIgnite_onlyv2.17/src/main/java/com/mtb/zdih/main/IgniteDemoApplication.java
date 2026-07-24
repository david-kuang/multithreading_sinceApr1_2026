package com.mtb.zdih.main;

import org.apache.ignite.Ignite;
import org.apache.ignite.IgniteCache;
import org.apache.ignite.Ignition;
import org.apache.ignite.cache.CacheAtomicityMode;
import org.apache.ignite.cache.CacheMode;
import org.apache.ignite.cluster.ClusterState;
import org.apache.ignite.configuration.*;
import org.jetbrains.annotations.NotNull;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class IgniteDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(IgniteDemoApplication.class, args);
    }

    private static @NotNull DataStorageConfiguration getDataStorageConfiguration() {
        DataRegionConfiguration drc = new DataRegionConfiguration();
        drc.setName("my-data-region");
        drc.setInitialSize(10 * 1024 * 1024);
        drc.setMaxSize(40 * 1024 * 1024);
        drc.setPageEvictionMode(DataPageEvictionMode.RANDOM_2_LRU);
        //drc.setPersistenceEnabled(false);
        Boolean getBooleanIsPersistenceEnabled = drc.isPersistenceEnabled();
        System.out.printf("Is DataRegionConfiguratrion PersistenceEnabled by default? %s;\n", getBooleanIsPersistenceEnabled);
        if (!getBooleanIsPersistenceEnabled) {
            drc.setPersistenceEnabled(true);
            System.out.printf("Set/Changed drc.isPersistenceEnabled() into %s.\n", drc.isPersistenceEnabled());
        }
        DataStorageConfiguration dsc = new DataStorageConfiguration();
        dsc.setDefaultDataRegionConfiguration(drc);

        return dsc;
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

    @Bean
    public ApplicationRunner applicationRunner(Ignite ignite) {
        return args -> {
            checkIGNITE_LOCAL_HOST(ignite);
            IgniteCache<String, String> cache = ignite.getOrCreateCache("dummy");
            //IgniteCache<String, String> cache9 = ignite.getOrCreateCache("cacheNumNine");
            //cache9.set
            //cache.put("key1", "value1");
            //cache.put("tdevyk3", "ykuang@mtb.com");
            /*cache.put("key1", "value1Jun18_2026");
            cache.put("tdevyk3", "ykuang@mtb.comAsOfJun18_2026");*/
            System.out.printf("cache.get(\"key1\") = %s, cache.get(\"tdevyk3\") = %s !\n", cache.get("key1"), cache.get("tdevyk3"));
        };
    }

    private static void checkIGNITE_LOCAL_HOST(Ignite ignite) {
        System.out.println("ENV IGNITE_LOCAL_HOST = " + System.getenv("IGNITE_LOCAL_HOST"));

        System.out.println("JVM IGNITE_LOCAL_HOST = " + System.getProperty("IGNITE_LOCAL_HOST"));

        System.out.println("Ignite localHost = " + ignite.configuration().getLocalHost());
    }

    private CacheConfiguration getCacheConfiguration() {
        CacheConfiguration<String, String> cc = new CacheConfiguration<>();
        cc.setName("dummy");
        cc.setOnheapCacheEnabled(false);
        cc.setBackups(1);

        config_CacheConfiguration_CacheMode_REPLICATED(cc);//#2
        CacheConfiguration_setStatisticsEnabled_True(cc);             //#3
        CacheConfiguration_setRebalanceOrder_1(cc);                 //#4
        CacheConfiguration_setRebalanceBatchSize_inBytes_mtb(cc);

        cc.setAtomicityMode(CacheAtomicityMode.TRANSACTIONAL);

        return cc;
    }

    private static void CacheConfiguration_setRebalanceBatchSize_inBytes_mtb(CacheConfiguration<String, String> cc) {
        System.out.printf("By default cc.getRebalanceBatchSize()[setRebalanceBatchSize is deprecated]=%s", cc.getRebalanceBatchSize());
        cc.setRebalanceBatchSize(2 * 1024 * 1024);
        System.out.printf("By default cc.getRebalanceBatchSize()[setRebalanceBatchSize is deprecated]=%s", cc.getRebalanceBatchSize());
    }

    private static void CacheConfiguration_setRebalanceOrder_1(CacheConfiguration<String, String> cc) {
        System.out.printf("By default cc.getRebalanceOrder()=%s. ", cc.getRebalanceOrder());
        cc.setRebalanceOrder(1);
        System.out.printf("After configuring, cc.getRebalanceOrder()=%s\n", cc.getRebalanceOrder());
    }

    private static void CacheConfiguration_setStatisticsEnabled_True(CacheConfiguration<String, String> cc) {
        System.out.printf("By default cc.isStatisticsEnabled()=%s. ", cc.isStatisticsEnabled());
        cc.setStatisticsEnabled(true);
        System.out.printf("After configuring, cc.isStatisticsEnabled()=%s\n", cc.isStatisticsEnabled());
    }

    private static void config_CacheConfiguration_CacheMode_REPLICATED(CacheConfiguration<String, String> cc) {
        System.out.printf("By default cc.getCacheMode()=%s. ", cc.getCacheMode());
        cc.setCacheMode(CacheMode.REPLICATED);
        System.out.printf("We explicitly config cc.getCacheMode() to %s\n", cc.getCacheMode());
    }
}
