import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
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

  profileImagePath(username: string): string {
    return `${environment.apiRoot}/media/profile_images/${username}.jpg`
  }
}
