CREATE INDEX "tracker_psiweightlog_imei_id_date" ON "tracker_psiweightlog" USING btree ("imei_id", "date");
CREATE INDEX "tracker_psiweightlog_imei_id_id" ON "tracker_psiweightlog" USING btree ("imei_id", "id");
CREATE INDEX "tracker_psiweightlog_sensor_date" ON "tracker_psiweightlog" USING btree ("sensor" , "date");
