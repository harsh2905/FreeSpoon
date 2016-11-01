-- MySQL dump 10.13  Distrib 5.5.49, for debian-linux-gnu (x86_64)
--
-- Host: db    Database: FreeSpoon
-- ------------------------------------------------------
-- Server version	5.7.13

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary table structure for view `view_history_purchased_products`
--

DROP TABLE IF EXISTS `view_history_purchased_products`;
/*!50001 DROP VIEW IF EXISTS `view_history_purchased_products`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `view_history_purchased_products` (
  `order_id` tinyint NOT NULL,
  `bulk_id` tinyint NOT NULL,
  `product_id` tinyint NOT NULL,
  `user_id` tinyint NOT NULL,
  `name` tinyint NOT NULL,
  `quantity` tinyint NOT NULL,
  `spec` tinyint NOT NULL,
  `create_time` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `view_history_purchased_products`
--

/*!50001 DROP TABLE IF EXISTS `view_history_purchased_products`*/;
/*!50001 DROP VIEW IF EXISTS `view_history_purchased_products`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `view_history_purchased_products` AS select `business_goods`.`order_id` AS `order_id`,`business_order`.`bulk_id` AS `bulk_id`,`business_goods`.`product_id` AS `product_id`,`business_user`.`id` AS `user_id`,`business_user`.`name` AS `name`,`business_goods`.`quantity` AS `quantity`,`business_product`.`spec` AS `spec`,`business_order`.`create_time` AS `create_time` from (((`business_goods` left join `business_order` on((`business_order`.`id` = `business_goods`.`order_id`))) left join `business_product` on((`business_goods`.`product_id` = `business_product`.`id`))) left join `business_user` on((`business_order`.`user_id` = `business_user`.`id`))) where ((`business_order`.`is_delete` = 0) and (`business_order`.`status` > 0)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-22 21:33:55
