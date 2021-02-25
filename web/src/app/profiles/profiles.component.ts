import { Component, OnInit } from '@angular/core';
import { APIService } from 'src/app/api.service';
import { Profile } from 'src/app/entities';
import { environment } from 'src/environments/environment';


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

  profileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`
  }
}
