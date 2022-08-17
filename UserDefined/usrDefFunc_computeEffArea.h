double Compute_effArea (int type_iso, double eta)
{
	double areaToReturn = 0;
	
	int   idxEta = -1;
	float rangeEta[] = {1.000, 1.479, 2.000, 2.200, 2.300, 2.400};
	
	
	double effArea[4][7] =
	{
		{0.0595, 0.0869, 0.0803, 0.0398, 0.0401, 0.0502, 0.0802},
		{0.0234, 0.0222, 0.0072, 0.0157, 0.0170, 0.0153, 0.0140},
		{0.1314, 0.1125, 0.0755, 0.1125, 0.1539, 0.1733, 0.1974},
		{0.1703, 0.1715, 0.1213, 0.1230, 0.1635, 0.1937, 0.2393}
	};
	
	for (int i=0; i<6; i++)
	{
		if (eta<rangeEta[i] && eta>=0)
		{
			idxEta = i;
			break;
		}
	}
	
	if (idxEta==-1 && eta>=0)
	{
		idxEta = 6;
	}
	
	
	areaToReturn = effArea[type_iso][idxEta];
	
	return areaToReturn;
}
