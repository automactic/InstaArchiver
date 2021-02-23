import { Component, OnInit } from '@angular/core';
import { APIService } from '../api.service';
import { Profile } from '../entities';

@Component({
  selector: 'app-profiles',
  templateUrl: './profiles.component.html',
  styleUrls: ['./profiles.component.scss']
})
export class ProfilesComponent implements OnInit {
  profiles: Profile[] = []
  constructor(private apiService: APIService) { }

  ngOnInit(): void {
    this.apiService.listProfiles().subscribe(data => {
      this.profiles = data.profiles
    })
  }
}
