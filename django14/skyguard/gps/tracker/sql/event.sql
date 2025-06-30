CREATE INDEX "tracker_event_imei_id_date_custom" ON "tracker_event" ("imei_id","date");
CREATE INDEX "tracker_event_imei_id_id_custom" ON "tracker_event" USING btree ("imei_id", "id");
