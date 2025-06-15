            # Create new device
            device = GPSDevice.objects.create(
                imei=imei,
                name=f"AUTO_{imei:015d}",
                comments=f"Auto-registered from email: {imei_data}"
            ) 