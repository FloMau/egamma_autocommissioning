double Compute_invariantMass (double pt1, double eta1, double phi1, double pt2, double eta2, double phi2)
{
	TLorentzVector v1;
	TLorentzVector v2;
	
	v1.SetPtEtaPhiM(pt1, eta1, phi1, 0.511*0.001);
	v2.SetPtEtaPhiM(pt2, eta2, phi2, 0.511*0.001);
	
	TLorentzVector z    = v1 + v2;
	
	double mass    = z.M();
	return mass;
}
